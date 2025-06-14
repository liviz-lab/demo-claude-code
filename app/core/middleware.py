import logging
import time
import uuid
from collections.abc import Awaitable, Callable

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.core.config import settings

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """リクエストログ出力ミドルウェア"""

    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        # リクエストIDを生成
        request_id = str(uuid.uuid4())

        # リクエスト開始時間
        start_time = time.time()

        # リクエスト情報をログ出力
        logger.info(
            f"[{request_id}] {request.method} {request.url} - "
            f"Client: {request.client.host if request.client else 'unknown'}"
        )

        # リクエストIDをヘッダーに追加
        request.state.request_id = request_id

        try:
            # レスポンス取得
            response = await call_next(request)

            # 処理時間計算
            process_time = time.time() - start_time

            # レスポンス情報をログ出力
            logger.info(f"[{request_id}] {response.status_code} - 処理時間: {process_time:.3f}s")

            # レスポンスヘッダーにリクエストIDを追加
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = str(process_time)

            return response

        except Exception as e:
            # エラー時の処理時間計算
            process_time = time.time() - start_time

            # エラーログ出力
            logger.error(f"[{request_id}] エラー: {type(e).__name__}: {e!s} - 処理時間: {process_time:.3f}s")

            # エラーレスポンス
            error_response = JSONResponse(
                status_code=500,
                content={
                    "error": "internal_error",
                    "message": "内部エラーが発生しました",
                    "status_code": 500,
                    "request_id": request_id,
                },
            )
            error_response.headers["X-Request-ID"] = request_id
            error_response.headers["X-Process-Time"] = str(process_time)

            return error_response


class CORSMiddleware(BaseHTTPMiddleware):
    """カスタムCORSミドルウェア"""

    def __init__(
        self,
        app: ASGIApp,
        allow_origins: list[str] | None = None,
        allow_methods: list[str] | None = None,
        allow_headers: list[str] | None = None,
    ):
        super().__init__(app)
        self.allow_origins = allow_origins or ["*"]
        self.allow_methods = allow_methods or ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
        self.allow_headers = allow_headers or ["*"]

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        # プリフライトリクエストの処理
        if request.method == "OPTIONS":
            response = Response()
            response.headers["Access-Control-Allow-Origin"] = ", ".join(self.allow_origins)
            response.headers["Access-Control-Allow-Methods"] = ", ".join(self.allow_methods)
            response.headers["Access-Control-Allow-Headers"] = ", ".join(self.allow_headers)
            response.headers["Access-Control-Max-Age"] = "86400"
            return response

        # 通常のリクエスト処理
        response = await call_next(request)

        # CORSヘッダーを追加
        response.headers["Access-Control-Allow-Origin"] = ", ".join(self.allow_origins)
        response.headers["Access-Control-Allow-Methods"] = ", ".join(self.allow_methods)
        response.headers["Access-Control-Allow-Headers"] = ", ".join(self.allow_headers)

        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """セキュリティヘッダー追加ミドルウェア"""

    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        response = await call_next(request)

        # セキュリティヘッダーを追加
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        return response


class APIKeyAuthMiddleware(BaseHTTPMiddleware):
    """API Key認証ミドルウェア"""

    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        # ヘルスチェックとルートエンドポイントは認証不要
        if request.url.path in ["/", "/docs", "/redoc", "/openapi.json"] or request.url.path.endswith("/health"):
            return await call_next(request)

        # API keyをヘッダーから取得
        api_key = request.headers.get(settings.AUTH_HEADER_NAME)

        # API keyが存在しない場合
        if not api_key:
            return JSONResponse(
                status_code=401,
                content={
                    "message": f"Missing required header: {settings.AUTH_HEADER_NAME}",
                    "code": "missing_api_key",
                    "detail": f"Please provide a valid API key in the {settings.AUTH_HEADER_NAME} header"
                }
            )

        # API keyが正しくない場合
        if api_key != settings.AUTH_HEADER_VALUE:
            return JSONResponse(
                status_code=401,
                content={
                    "message": "Invalid API key",
                    "code": "invalid_api_key",
                    "detail": "The provided API key is not valid"
                }
            )

        # API keyが正しい場合、リクエストを続行
        return await call_next(request)
