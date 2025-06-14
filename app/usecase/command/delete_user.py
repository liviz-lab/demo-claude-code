from app.core.error import UserNotFoundError
from app.ports.user_repository import UserRepository


class DeleteUserUseCase:
    """ユーザー削除ユースケース"""

    def __init__(self, user_repository: UserRepository):
        self._user_repository = user_repository

    def execute(self, user_id: int) -> int:
        """
        ユーザーを削除する

        Args:
            user_id: ユーザーID

        Returns:
            int: 削除されたユーザーID

        Raises:
            UserNotFoundError: ユーザーが見つからない場合
        """
        # ユーザーの存在確認
        user = self._user_repository.find_by_id(user_id)
        if not user:
            raise UserNotFoundError(user_id)

        # ユーザー削除
        success = self._user_repository.delete(user_id)
        if not success:
            raise UserNotFoundError(user_id)

        return user_id
