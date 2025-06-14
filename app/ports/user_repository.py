from abc import ABC, abstractmethod

from app.domain.entities import User


class UserRepository(ABC):
    """ユーザーリポジトリインターフェース"""

    @abstractmethod
    def create(self, name: str, email: str, age: int) -> User:
        """ユーザーを作成"""
        pass

    @abstractmethod
    def find_by_id(self, user_id: int) -> User | None:
        """IDでユーザーを取得"""
        pass

    @abstractmethod
    def find_by_email(self, email: str) -> User | None:
        """メールアドレスでユーザーを取得"""
        pass

    @abstractmethod
    def find_all(
        self,
        name: str | None = None,
        min_age: int | None = None,
        max_age: int | None = None,
        limit: int = 10,
        offset: int = 0,
    ) -> tuple[list[User], int]:
        """ユーザーリストを取得"""
        pass

    @abstractmethod
    def update(
        self, user_id: int, name: str | None = None, email: str | None = None, age: int | None = None
    ) -> User | None:
        """ユーザーを更新"""
        pass

    @abstractmethod
    def delete(self, user_id: int) -> bool:
        """ユーザーを削除"""
        pass

    @abstractmethod
    def exists_by_email(self, email: str, exclude_user_id: int | None = None) -> bool:
        """メールアドレスの存在確認"""
        pass
