import logging

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from app.api.endpoints import router as api_router
from app.core.config import settings
from app.core.error import (
    CustomHTTPException,
    custom_http_exception_handler,
    general_exception_handler,
    validation_exception_handler,
)
from app.core.middleware import APIKeyAuthMiddleware, RequestLoggingMiddleware, SecurityHeadersMiddleware

# ログ設定
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# FastAPIアプリケーション作成
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    description="FastAPI ミドルウェア検証用デモアプリケーション",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ミドルウェア設定
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(APIKeyAuthMiddleware)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 例外ハンドラー設定
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(CustomHTTPException, custom_http_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# ルーター設定
app.include_router(api_router, prefix=settings.API_V1_STR, tags=["users"])


# ルートエンドポイント
@app.get("/")
async def root() -> dict[str, str]:
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": f"{settings.API_V1_STR}/health",
    }


def main() -> None:
    import uvicorn

    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)


if __name__ == "__main__":
    main()
