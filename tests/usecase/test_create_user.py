import pytest

from app.core.error import EmailDuplicateError
from app.infra.user_repository_impl import InMemoryUserRepository
from app.usecase.command.create_user import CreateUserUseCase
from schemas.requests.user import UserCreateRequest


class TestCreateUserUseCase:
    """ユーザー作成ユースケースのテスト"""

    @pytest.mark.unit
    def test_create_user_success(self, test_user_repository: InMemoryUserRepository) -> None:
        """ユーザー作成成功テスト"""
        usecase = CreateUserUseCase(test_user_repository)
        request = UserCreateRequest(name="テストユーザー", email="test@example.com", age=25)

        user = usecase.execute(request)

        assert user.id == 1
        assert user.name == "テストユーザー"
        assert user.email == "test@example.com"
        assert user.age == 25

    @pytest.mark.unit
    def test_create_user_duplicate_email(self, test_user_repository: InMemoryUserRepository) -> None:
        """重複メールアドレスでユーザー作成テスト"""
        usecase = CreateUserUseCase(test_user_repository)
        request = UserCreateRequest(name="テストユーザー", email="test@example.com", age=25)

        # 最初のユーザーを作成
        usecase.execute(request)

        # 同じメールアドレスで再度作成を試行
        with pytest.raises(EmailDuplicateError) as exc_info:
            usecase.execute(request)

        assert "test@example.com" in str(exc_info.value.detail)
