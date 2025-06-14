from app.core.error import EmailDuplicateError
from app.domain.entities import User
from app.ports.user_repository import UserRepository
from schemas.requests.user import UserCreateRequest


class CreateUserUseCase:
    """ユーザー作成ユースケース"""

    def __init__(self, user_repository: UserRepository):
        self._user_repository = user_repository

    def execute(self, request: UserCreateRequest) -> User:
        """
        ユーザーを作成する

        Args:
            request: ユーザー作成リクエスト

        Returns:
            User: 作成されたユーザーエンティティ

        Raises:
            EmailDuplicateError: メールアドレスが重複している場合
        """
        # メールアドレスの重複チェック
        if self._user_repository.exists_by_email(request.email):
            raise EmailDuplicateError(request.email)

        # ユーザー作成
        return self._user_repository.create(name=request.name, email=request.email, age=request.age)
