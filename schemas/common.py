from pydantic import BaseModel, Field


class PaginationBase(BaseModel):
    """ページネーション基底クラス"""

    limit: int = Field(10, ge=1, le=100, description="取得件数")
    offset: int = Field(0, ge=0, description="オフセット")


class SearchBase(BaseModel):
    """検索条件基底クラス"""

    name: str | None = Field(None, description="名前で検索")


class AgeFilterBase(BaseModel):
    """年齢フィルター基底クラス"""

    min_age: int | None = Field(None, ge=0, description="最小年齢")
    max_age: int | None = Field(None, le=120, description="最大年齢")


class PaginationResponseBase(BaseModel):
    """ページネーションレスポンス基底クラス"""

    total: int = Field(..., description="総件数")
    limit: int = Field(..., description="リミット")
    offset: int = Field(..., description="オフセット")


class ApiResponseBase(BaseModel):
    """API共通レスポンス基底クラス"""

    message: str = Field(..., description="メッセージ")


class ApiErrorBase(BaseModel):
    """APIエラー基底クラス"""

    message: str = Field(..., description="エラーメッセージ")
    code: str = Field(..., description="エラーコード")
    detail: str | None = Field(None, description="エラー詳細")
