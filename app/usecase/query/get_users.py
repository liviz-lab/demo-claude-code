from app.domain.entities import User
from app.ports.user_repository import UserRepository
from schemas.requests.user import UsersQuery


class GetUsersUseCase:
    """ユーザーリスト取得ユースケース"""

    def __init__(self, user_repository: UserRepository):
        self._user_repository = user_repository

    def execute(self, query: UsersQuery) -> tuple[list[User], int]:
        """
        ユーザーリストを取得する

        Args:
            query: ユーザーリスト取得クエリ

        Returns:
            tuple[list[User], int]: ユーザーリストと総件数
        """
        return self._user_repository.find_all(
            name=query.name, min_age=query.min_age, max_age=query.max_age, limit=query.limit, offset=query.offset
        )
