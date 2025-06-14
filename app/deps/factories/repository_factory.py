from app.infra.user_repository_impl import InMemoryUserRepository
from app.ports.user_repository import UserRepository

# シングルトンインスタンス
_user_repository_instance = None


def get_user_repository() -> UserRepository:
    """ユーザーリポジトリの依存性注入"""
    global _user_repository_instance
    if _user_repository_instance is None:
        _user_repository_instance = InMemoryUserRepository()
    return _user_repository_instance
