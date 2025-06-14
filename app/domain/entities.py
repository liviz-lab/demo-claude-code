from datetime import datetime


class User:
    """ユーザーエンティティ"""

    def __init__(self, id: int, name: str, email: str, age: int):
        self.id = id
        self.name = name
        self.email = email
        self.age = age
        now = datetime.now()
        self.created_at = now
        self.updated_at = now

    def update(self, name: str | None = None, email: str | None = None, age: int | None = None) -> None:
        """ユーザー情報を更新"""
        if name is not None:
            self.name = name
        if email is not None:
            self.email = email
        if age is not None:
            self.age = age
        self.updated_at = datetime.now()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, User):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)
