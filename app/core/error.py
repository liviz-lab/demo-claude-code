import logging

from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.core.error_codes import (
    AUTH_ERROR_CODE,
    AUTH_ERROR_MESSAGE,
    EMAIL_DUPLICATE_CODE,
    EMAIL_DUPLICATE_MESSAGE,
    INTERNAL_ERROR_CODE,
    INTERNAL_ERROR_MESSAGE,
    NOT_FOUND_CODE,
    NOT_FOUND_MESSAGE,
    USER_NOT_FOUND_CODE,
    USER_NOT_FOUND_MESSAGE,
    VALIDATION_ERROR_CODE,
    VALIDATION_ERROR_MESSAGE,
)
from schemas.responses.error import (
    AuthErrorResponse,
    ErrorResponse,
    InternalErrorResponse,
    NotFoundErrorResponse,
    ValidationErrorDetail,
    ValidationErrorResponse,
)

logger = logging.getLogger(__name__)


class CustomHTTPException(HTTPException):
    """カスタムHTTP例外"""

    def __init__(self, status_code: int, code: str, message: str, detail: str | None = None):
        self.status_code = status_code
        self.code = code
        self.message = message
        super().__init__(status_code=status_code, detail=detail or message)
        # HTTPException sets self.detail to message, so we override it after
        self.detail = detail or message


class AuthenticationError(CustomHTTPException):
    """認証エラー"""

    def __init__(self, message: str = AUTH_ERROR_MESSAGE, detail: str | None = None):
        super().__init__(status_code=401, code=AUTH_ERROR_CODE, message=message, detail=detail)


class NotFoundError(CustomHTTPException):
    """リソースが見つからないエラー"""

    def __init__(self, message: str = NOT_FOUND_MESSAGE, detail: str | None = None):
        super().__init__(status_code=404, code=NOT_FOUND_CODE, message=message, detail=detail)


class UserNotFoundError(CustomHTTPException):
    """ユーザーが見つからないエラー"""

    def __init__(self, user_id: int):
        super().__init__(
            status_code=404, code=USER_NOT_FOUND_CODE, message=USER_NOT_FOUND_MESSAGE, detail=f"ユーザーID: {user_id}"
        )


class ValidationErrorException(CustomHTTPException):
    """バリデーションエラー"""

    def __init__(self, message: str = VALIDATION_ERROR_MESSAGE, detail: str | None = None):
        super().__init__(status_code=422, code=VALIDATION_ERROR_CODE, message=message, detail=detail)


class EmailDuplicateError(CustomHTTPException):
    """メールアドレス重複エラー"""

    def __init__(self, email: str):
        super().__init__(
            status_code=422,
            code=EMAIL_DUPLICATE_CODE,
            message=EMAIL_DUPLICATE_MESSAGE,
            detail=f"メールアドレス: {email}",
        )


def convert_validation_error_to_details(error: ValidationError | RequestValidationError) -> list[ValidationErrorDetail]:
    """PydanticのValidationErrorを詳細エラー形式に変換"""
    details: list[ValidationErrorDetail] = []
    for err in error.errors():
        detail = ValidationErrorDetail(
            loc=[str(loc) for loc in err.get("loc", [])],
            msg=err.get("msg", ""),
            type=err.get("type", ""),
            ctx=err.get("ctx"),
        )
        details.append(detail)
    return details


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """バリデーションエラーハンドラー"""
    details = convert_validation_error_to_details(exc)

    # エラーの詳細を生成
    missing_fields = []
    invalid_values = []

    for err in exc.errors():
        error_type = err.get("type", "")
        location = " -> ".join(str(loc) for loc in err.get("loc", []))
        input_value = err.get("input")

        if error_type in ["missing", "value_error.missing"]:
            missing_fields.append(location)
        else:
            invalid_values.append(f"{location}: {input_value}")

    # エラーメッセージを構築
    detail_parts = []
    if missing_fields:
        detail_parts.append(f"必須項目が不足しています: {', '.join(missing_fields)}")
    if invalid_values:
        detail_parts.append(f"入力値が不正です: {', '.join(invalid_values)}")

    detail_message = "; ".join(detail_parts) if detail_parts else "入力値を確認してください"

    error_response = ValidationErrorResponse(
        message="リクエストのバリデーションに失敗しました",
        code=VALIDATION_ERROR_CODE,
        detail=detail_message,
        details=details,
    )

    logger.warning(f"Validation error: {exc}")
    return JSONResponse(status_code=422, content=error_response.model_dump())


async def custom_http_exception_handler(request: Request, exc: CustomHTTPException) -> JSONResponse:
    """カスタムHTTP例外ハンドラー"""
    error_response: AuthErrorResponse | NotFoundErrorResponse | ValidationErrorResponse | ErrorResponse
    
    if isinstance(exc, AuthenticationError):
        error_response = AuthErrorResponse(message=exc.message, code=exc.code, detail=exc.detail)
    elif isinstance(exc, NotFoundError | UserNotFoundError):
        error_response = NotFoundErrorResponse(message=exc.message, code=exc.code, detail=exc.detail)
    elif isinstance(exc, ValidationErrorException | EmailDuplicateError):
        error_response = ValidationErrorResponse(message=exc.message, code=exc.code, detail=exc.detail, details=None)
    else:
        error_response = ErrorResponse(message=exc.message, code=exc.code, detail=exc.detail)

    logger.error(f"Custom HTTP exception: {exc.code} - {exc.message}")
    return JSONResponse(status_code=exc.status_code, content=error_response.model_dump())


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """一般的な例外ハンドラー"""
    error_response = InternalErrorResponse(
        message=INTERNAL_ERROR_MESSAGE, code=INTERNAL_ERROR_CODE, detail=f"{type(exc).__name__}: {exc!s}"
    )

    logger.error(f"General exception: {type(exc).__name__} - {exc!s}")
    return JSONResponse(status_code=500, content=error_response.model_dump())
