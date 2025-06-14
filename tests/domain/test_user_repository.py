import pytest

from app.infra.user_repository_impl import InMemoryUserRepository
from app.ports.user_repository import UserRepository


class TestInMemoryUserRepository:
    """InMemoryUserRepositoryの実装テスト"""

    @pytest.mark.unit
    def test_implements_interface(self) -> None:
        """UserRepositoryインターフェースを実装していることを確認"""
        repo = InMemoryUserRepository()
        assert isinstance(repo, UserRepository)

    @pytest.mark.unit
    def test_exists_by_email(self, test_user_repository: InMemoryUserRepository) -> None:
        """メールアドレス存在確認テスト"""
        # 初期状態では存在しない
        assert not test_user_repository.exists_by_email("test@example.com")

        # ユーザー作成後は存在する
        test_user_repository.create("テストユーザー", "test@example.com", 25)
        assert test_user_repository.exists_by_email("test@example.com")

        # 異なるメールアドレスは存在しない
        assert not test_user_repository.exists_by_email("other@example.com")

    @pytest.mark.unit
    def test_exists_by_email_with_exclusion(self, test_user_repository: InMemoryUserRepository) -> None:
        """除外付きメールアドレス存在確認テスト"""
        user = test_user_repository.create("テストユーザー", "test@example.com", 25)

        # 除外なしでは存在する
        assert test_user_repository.exists_by_email("test@example.com")

        # 自分のIDを除外すると存在しない
        assert not test_user_repository.exists_by_email("test@example.com", exclude_user_id=user.id)

        # 他のIDを除外すると存在する
        assert test_user_repository.exists_by_email("test@example.com", exclude_user_id=999)
