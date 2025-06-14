from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class UserResponse(BaseModel):
    id: int = Field(..., description="ユーザーID")
    name: str = Field(..., description="ユーザー名")
    email: str = Field(..., description="メールアドレス")
    age: int = Field(..., description="年齢")
    created_at: datetime = Field(..., description="作成日時")
    updated_at: datetime = Field(..., description="更新日時")

    model_config = ConfigDict(from_attributes=True)


class UserListResponse(BaseModel):
    users: list[UserResponse] = Field(..., description="ユーザーリスト")
    total: int = Field(..., description="総件数")
    limit: int = Field(..., description="リミット")
    offset: int = Field(..., description="オフセット")


class UserCreateResponse(BaseModel):
    message: str = Field(..., description="メッセージ")
    user: UserResponse = Field(..., description="作成されたユーザー")


class UserUpdateResponse(BaseModel):
    message: str = Field(..., description="メッセージ")
    user: UserResponse = Field(..., description="更新されたユーザー")


class UserDeleteResponse(BaseModel):
    message: str = Field(..., description="メッセージ")
    deleted_user_id: int = Field(..., description="削除されたユーザーID")
