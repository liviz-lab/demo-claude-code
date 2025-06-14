from fastapi import Depends

from app.core.error import NotFoundError
from app.deps.db import InMemoryDatabase, User, get_database
from schemas.requests.user import UserCreateRequest, UsersQuery, UserUpdateRequest
from schemas.responses.user import UserResponse


class UserFactory:
    """ユーザー関連のビジネスロジックを担当するファクトリークラス"""

    def __init__(self, db: InMemoryDatabase = Depends(get_database)):
        self.db = db

    def create_user(self, request: UserCreateRequest) -> User:
        """ユーザーを作成"""
        # 既存のメールアドレスチェック
        existing_user = self.db.get_user_by_email(request.email)
        if existing_user:
            raise ValueError("このメールアドレスは既に使用されています")

        return self.db.create_user(name=request.name, email=request.email, age=request.age)

    def get_user_by_id(self, user_id: int) -> User:
        """IDでユーザーを取得"""
        user = self.db.get_user_by_id(user_id)
        if not user:
            raise NotFoundError(f"ID {user_id} のユーザーが見つかりません")
        return user

    def get_users(self, query: UsersQuery) -> tuple[list[User], int]:
        """ユーザーリストを取得"""
        return self.db.get_users(
            name=query.name, min_age=query.min_age, max_age=query.max_age, limit=query.limit, offset=query.offset
        )

    def update_user(self, user_id: int, request: UserUpdateRequest) -> User:
        """ユーザーを更新"""
        # ユーザーの存在確認
        user = self.get_user_by_id(user_id)

        # メールアドレスの重複チェック
        if request.email and request.email != user.email:
            existing_user = self.db.get_user_by_email(request.email)
            if existing_user and existing_user.id != user_id:
                raise ValueError("このメールアドレスは既に使用されています")

        updated_user = self.db.update_user(user_id=user_id, name=request.name, email=request.email, age=request.age)

        if not updated_user:
            raise NotFoundError(f"ID {user_id} のユーザーが見つかりません")

        return updated_user

    def delete_user(self, user_id: int) -> int:
        """ユーザーを削除"""
        # ユーザーの存在確認
        self.get_user_by_id(user_id)

        success = self.db.delete_user(user_id)
        if not success:
            raise NotFoundError(f"ID {user_id} のユーザーが見つかりません")

        return user_id

    @staticmethod
    def convert_to_response(user: User) -> UserResponse:
        """UserモデルをUserResponseに変換"""
        return UserResponse(
            id=user.id,
            name=user.name,
            email=user.email,
            age=user.age,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )


def get_user_factory(db: InMemoryDatabase = Depends(get_database)) -> UserFactory:
    """UserFactoryの依存性注入"""
    return UserFactory(db=db)
