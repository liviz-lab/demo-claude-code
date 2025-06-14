import threading
from datetime import datetime


class User:
    """インメモリ用のユーザーモデル"""

    def __init__(self, id: int, name: str, email: str, age: int):
        self.id = id
        self.name = name
        self.email = email
        self.age = age
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

    def update(self, name: str | None = None, email: str | None = None, age: int | None = None) -> None:
        if name is not None:
            self.name = name
        if email is not None:
            self.email = email
        if age is not None:
            self.age = age
        self.updated_at = datetime.now()


class InMemoryDatabase:
    """インメモリデータベース（スレッドセーフ）"""

    def __init__(self) -> None:
        self._users: dict[int, User] = {}
        self._user_counter = 0
        self._lock = threading.Lock()

    def create_user(self, name: str, email: str, age: int) -> User:
        with self._lock:
            self._user_counter += 1
            user = User(id=self._user_counter, name=name, email=email, age=age)
            self._users[user.id] = user
            return user

    def get_user_by_id(self, user_id: int) -> User | None:
        return self._users.get(user_id)

    def get_user_by_email(self, email: str) -> User | None:
        for user in self._users.values():
            if user.email == email:
                return user
        return None

    def get_users(
        self,
        name: str | None = None,
        min_age: int | None = None,
        max_age: int | None = None,
        limit: int = 10,
        offset: int = 0,
    ) -> tuple[list[User], int]:
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

    def update_user(
        self, user_id: int, name: str | None = None, email: str | None = None, age: int | None = None
    ) -> User | None:
        user = self.get_user_by_id(user_id)
        if user:
            user.update(name=name, email=email, age=age)
        return user

    def delete_user(self, user_id: int) -> bool:
        with self._lock:
            if user_id in self._users:
                del self._users[user_id]
                return True
            return False

    def clear_all(self) -> None:
        """テスト用：全データを削除"""
        with self._lock:
            self._users.clear()
            self._user_counter = 0


# シングルトンインスタンス
_db_instance = None


def get_database() -> InMemoryDatabase:
    """データベースインスタンスを取得（依存性注入用）"""
    global _db_instance
    if _db_instance is None:
        _db_instance = InMemoryDatabase()
    return _db_instance
