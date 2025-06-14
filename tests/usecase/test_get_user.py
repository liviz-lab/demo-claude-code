import pytest

from app.core.error import UserNotFoundError
from app.infra.user_repository_impl import InMemoryUserRepository
from app.usecase.query.get_user import GetUserUseCase


class TestGetUserUseCase:
    """ユーザー詳細取得ユースケースのテスト"""

    @pytest.mark.unit
    def test_get_user_success(self, test_user_repository: InMemoryUserRepository) -> None:
        """ユーザー取得成功テスト"""
        usecase = GetUserUseCase(test_user_repository)

        # テストユーザーを作成
        created_user = test_user_repository.create("テストユーザー", "test@example.com", 25)

        # ユーザーを取得
        user = usecase.execute(created_user.id)

        assert user.id == created_user.id
        assert user.name == "テストユーザー"
        assert user.email == "test@example.com"
        assert user.age == 25

    @pytest.mark.unit
    def test_get_user_not_found(self, test_user_repository: InMemoryUserRepository) -> None:
        """存在しないユーザー取得テスト"""
        usecase = GetUserUseCase(test_user_repository)

        with pytest.raises(UserNotFoundError) as exc_info:
            usecase.execute(999)

        assert exc_info.value.status_code == 404
        assert "999" in str(exc_info.value.detail)
