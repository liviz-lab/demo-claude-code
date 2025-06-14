import threading

from app.domain.entities import User
from app.ports.user_repository import UserRepository


class InMemoryUserRepository(UserRepository):
    """インメモリユーザーリポジトリ実装"""

    def __init__(self) -> None:
        self._users: dict[int, User] = {}
        self._user_counter = 0
        self._lock = threading.Lock()

    def create(self, name: str, email: str, age: int) -> User:
        """ユーザーを作成"""
        with self._lock:
            self._user_counter += 1
            user = User(id=self._user_counter, name=name, email=email, age=age)
            self._users[user.id] = user
            return user

    def find_by_id(self, user_id: int) -> User | None:
        """IDでユーザーを取得"""
        return self._users.get(user_id)

    def find_by_email(self, email: str) -> User | None:
        """メールアドレスでユーザーを取得"""
        for user in self._users.values():
            if user.email == email:
                return user
        return None

    def find_all(
        self,
        name: str | None = None,
        min_age: int | None = None,
        max_age: int | None = None,
        limit: int = 10,
        offset: int = 0,
    ) -> tuple[list[User], int]:
        """ユーザーリストを取得"""
        users = list(self._users.values())

        # フィルタリング
        if name:
            users = [u for u in users if name.lower() in u.name.lower()]
        if min_age is not None:
            users = [u for u in users if u.age >= min_age]
        if max_age is not None:
            users = [u for u in users if u.age <= max_age]

        total = len(users)

        # ページネーション
        users = users[offset : offset + limit]

        return users, total

    def update(
        self, user_id: int, name: str | None = None, email: str | None = None, age: int | None = None
    ) -> User | None:
        """ユーザーを更新"""
        user = self.find_by_id(user_id)
        if user:
            user.update(name=name, email=email, age=age)
        return user

    def delete(self, user_id: int) -> bool:
        """ユーザーを削除"""
        with self._lock:
            if user_id in self._users:
                del self._users[user_id]
                return True
            return False

    def exists_by_email(self, email: str, exclude_user_id: int | None = None) -> bool:
        """メールアドレスの存在確認"""
        for user in self._users.values():
            if user.email == email and (exclude_user_id is None or user.id != exclude_user_id):
                return True
        return False

    def clear_all(self) -> None:
        """テスト用：全データを削除"""
        with self._lock:
            self._users.clear()
            self._user_counter = 0
