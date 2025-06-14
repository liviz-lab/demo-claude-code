from app.ports.user_repository import UserRepository


class UserDomainService:
    """ユーザードメインサービス"""

    def __init__(self, user_repository: UserRepository):
        self._user_repository = user_repository

    def is_email_available(self, email: str, exclude_user_id: int | None = None) -> bool:
        """
        メールアドレスが利用可能かチェックする

        Args:
            email: チェックするメールアドレス
            exclude_user_id: 除外するユーザーID（更新時に使用）

        Returns:
            bool: 利用可能な場合True
        """
        return not self._user_repository.exists_by_email(email, exclude_user_id)

    def validate_user_uniqueness(self, email: str, exclude_user_id: int | None = None) -> None:
        """
        ユーザーの一意性をバリデーションする

        Args:
            email: チェックするメールアドレス
            exclude_user_id: 除外するユーザーID（更新時に使用）

        Raises:
            ValueError: メールアドレスが重複している場合
        """
        if not self.is_email_available(email, exclude_user_id):
            raise ValueError("このメールアドレスは既に使用されています")
