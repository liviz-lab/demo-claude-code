from typing import Any

from pydantic import BaseModel, Field

from schemas.common import ApiErrorBase


class ValidationErrorDetail(BaseModel):
    loc: list[str] = Field(..., description="エラーの場所")
    msg: str = Field(..., description="エラーメッセージ")
    type: str = Field(..., description="エラータイプ")
    ctx: dict[str, Any] | None = Field(None, description="エラーコンテキスト")


class ErrorResponse(ApiErrorBase):
    """新しいエラーレスポンス形式"""

    pass


class ValidationErrorResponse(ApiErrorBase):
    """バリデーションエラーレスポンス"""

    details: list[ValidationErrorDetail] | None = Field(None, description="詳細エラー情報")


class AuthErrorResponse(ApiErrorBase):
    """認証エラーレスポンス"""

    pass


class NotFoundErrorResponse(ApiErrorBase):
    """リソースが見つからないエラーレスポンス"""

    pass


class InternalErrorResponse(ApiErrorBase):
    """内部エラーレスポンス"""

    pass
