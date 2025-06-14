from pydantic import BaseModel, Field

from schemas.common import AgeFilterBase, PaginationBase, SearchBase


class UserCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="ユーザー名")
    email: str = Field(..., pattern=r"^[^@]+@[^@]+\.[^@]+$", description="メールアドレス")
    age: int = Field(..., ge=0, le=120, description="年齢")


class UserUpdateRequest(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100, description="ユーザー名")
    email: str | None = Field(None, pattern=r"^[^@]+@[^@]+\.[^@]+$", description="メールアドレス")
    age: int | None = Field(None, ge=0, le=120, description="年齢")


class UsersQuery(PaginationBase, SearchBase, AgeFilterBase):
    """ユーザーリスト取得クエリ"""

    pass


class UserQuery(BaseModel):
    """単一ユーザー取得クエリ"""

    user_id: int = Field(..., ge=1, description="ユーザーID")
