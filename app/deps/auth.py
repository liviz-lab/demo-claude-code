from fastapi import Depends, Header

from app.core.config import settings
from app.core.error import AuthenticationError


def verify_api_key(x_api_key: str | None = Header(None, alias=settings.AUTH_HEADER_NAME)) -> str:
    """
    API キーを検証する依存性

    Args:
        x_api_key: APIキーヘッダー

    Returns:
        str: 検証済みのAPIキー

    Raises:
        AuthenticationError: 認証に失敗した場合
    """
    if not x_api_key:
        raise AuthenticationError(f"必須ヘッダー '{settings.AUTH_HEADER_NAME}' が見つかりません")

    if x_api_key != settings.AUTH_HEADER_VALUE:
        raise AuthenticationError("無効なAPIキーです")

    return x_api_key


