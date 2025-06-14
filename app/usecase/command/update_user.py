from app.core.error import EmailDuplicateError, UserNotFoundError
from app.domain.entities import User
from app.ports.user_repository import UserRepository
from schemas.requests.user import UserUpdateRequest


class UpdateUserUseCase:
    """ユーザー更新ユースケース"""

    def __init__(self, user_repository: UserRepository):
        self._user_repository = user_repository

    def execute(self, user_id: int, request: UserUpdateRequest) -> User:
        """
        ユーザーを更新する

        Args:
            user_id: ユーザーID
            request: ユーザー更新リクエスト

        Returns:
            User: 更新されたユーザーエンティティ

        Raises:
            UserNotFoundError: ユーザーが見つからない場合
            EmailDuplicateError: メールアドレスが重複している場合
        """
        # ユーザーの存在確認
        user = self._user_repository.find_by_id(user_id)
        if not user:
            raise UserNotFoundError(user_id)

        # メールアドレスの重複チェック
        if request.email and self._user_repository.exists_by_email(request.email, exclude_user_id=user_id):
            raise EmailDuplicateError(request.email)

        # ユーザー更新
        updated_user = self._user_repository.update(
            user_id=user_id, name=request.name, email=request.email, age=request.age
        )

        if not updated_user:
            raise UserNotFoundError(user_id)

        return updated_user
