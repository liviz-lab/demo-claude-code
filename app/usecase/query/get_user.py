from app.core.error import UserNotFoundError
from app.domain.entities import User
from app.ports.user_repository import UserRepository


class GetUserUseCase:
    """ユーザー詳細取得ユースケース"""

    def __init__(self, user_repository: UserRepository):
        self._user_repository = user_repository

    def execute(self, user_id: int) -> User:
        """
        ユーザー詳細を取得する

        Args:
            user_id: ユーザーID

        Returns:
            User: ユーザーエンティティ

        Raises:
            UserNotFoundError: ユーザーが見つからない場合
        """
        user = self._user_repository.find_by_id(user_id)
        if not user:
            raise UserNotFoundError(user_id)
        return user
