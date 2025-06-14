from datetime import datetime

import pytest

from app.domain.entities import User
from app.infra.user_repository_impl import InMemoryUserRepository


class TestUser:
    """Userモデルのテスト"""

    @pytest.mark.unit
    def test_user_creation(self) -> None:
        """ユーザー作成テスト"""
        user = User(id=1, name="テストユーザー", email="test@example.com", age=25)

        assert user.id == 1
        assert user.name == "テストユーザー"
        assert user.email == "test@example.com"
        assert user.age == 25
        assert isinstance(user.created_at, datetime)
        assert isinstance(user.updated_at, datetime)
        assert user.created_at == user.updated_at

    @pytest.mark.unit
    def test_user_update(self) -> None:
        """ユーザー更新テスト"""
        user = User(id=1, name="テストユーザー", email="test@example.com", age=25)
        original_created_at = user.created_at
        original_updated_at = user.updated_at

        # 少し待機してから更新
        import time

        time.sleep(0.01)

        user.update(name="更新後ユーザー", age=30)

        assert user.name == "更新後ユーザー"
        assert user.email == "test@example.com"  # 変更されていない
        assert user.age == 30
        assert user.created_at == original_created_at  # 変更されていない
        assert user.updated_at > original_updated_at  # 更新されている

    @pytest.mark.unit
    def test_user_partial_update(self) -> None:
        """ユーザー部分更新テスト"""
        user = User(id=1, name="テストユーザー", email="test@example.com", age=25)

        # 名前のみ更新
        user.update(name="新しい名前")

        assert user.name == "新しい名前"
        assert user.email == "test@example.com"
        assert user.age == 25


class TestInMemoryUserRepository:
    """InMemoryUserRepositoryのテスト"""

    @pytest.mark.unit
    def test_repository_initialization(self) -> None:
        """リポジトリ初期化テスト"""
        repo = InMemoryUserRepository()

        assert repo._user_counter == 0
        assert len(repo._users) == 0

    @pytest.mark.unit
    def test_create(self, test_user_repository: InMemoryUserRepository) -> None:
        """ユーザー作成テスト"""
        user = test_user_repository.create(name="テストユーザー", email="test@example.com", age=25)

        assert user.id == 1
        assert user.name == "テストユーザー"
        assert user.email == "test@example.com"
        assert user.age == 25
        assert test_user_repository._user_counter == 1
        assert len(test_user_repository._users) == 1

    @pytest.mark.unit
    def test_create_multiple_users(self, test_user_repository: InMemoryUserRepository) -> None:
        """複数ユーザー作成テスト"""
        user1 = test_user_repository.create(name="ユーザー1", email="user1@example.com", age=25)
        user2 = test_user_repository.create(name="ユーザー2", email="user2@example.com", age=30)

        assert user1.id == 1
        assert user2.id == 2
        assert test_user_repository._user_counter == 2
        assert len(test_user_repository._users) == 2

    @pytest.mark.unit
    def test_find_by_id(self, test_user_repository: InMemoryUserRepository) -> None:
        """IDでユーザー取得テスト"""
        created_user = test_user_repository.create(name="テストユーザー", email="test@example.com", age=25)

        # 存在するユーザーを取得
        user = test_user_repository.find_by_id(created_user.id)
        assert user is not None
        assert user.id == created_user.id
        assert user.name == created_user.name

        # 存在しないユーザーを取得
        user = test_user_repository.find_by_id(999)
        assert user is None

    @pytest.mark.unit
    def test_find_by_email(self, test_user_repository: InMemoryUserRepository) -> None:
        """メールアドレスでユーザー取得テスト"""
        created_user = test_user_repository.create(name="テストユーザー", email="test@example.com", age=25)

        # 存在するメールアドレスで取得
        user = test_user_repository.find_by_email("test@example.com")
        assert user is not None
        assert user.email == created_user.email
        assert user.name == created_user.name

        # 存在しないメールアドレスで取得
        user = test_user_repository.find_by_email("notfound@example.com")
        assert user is None

    @pytest.mark.unit
    def test_find_all_empty(self, test_user_repository: InMemoryUserRepository) -> None:
        """空のユーザーリスト取得テスト"""
        users, total = test_user_repository.find_all()

        assert users == []
        assert total == 0

    @pytest.mark.unit
    def test_find_all_basic(self, populated_repository: InMemoryUserRepository) -> None:
        """基本のユーザーリスト取得テスト"""
        users, total = populated_repository.find_all()

        assert len(users) == 5
        assert total == 5

    @pytest.mark.unit
    def test_find_all_with_name_filter(self, populated_repository: InMemoryUserRepository) -> None:
        """名前フィルターでユーザーリスト取得テスト"""
        users, total = populated_repository.find_all(name="田中")

        assert len(users) == 1
        assert total == 1
        assert "田中" in users[0].name

    @pytest.mark.unit
    def test_find_all_with_age_filter(self, populated_repository: InMemoryUserRepository) -> None:
        """年齢フィルターでユーザーリスト取得テスト"""
        # 最小年齢フィルター
        users, total = populated_repository.find_all(min_age=30)
        assert all(user.age >= 30 for user in users)

        # 最大年齢フィルター
        users, total = populated_repository.find_all(max_age=25)
        assert all(user.age <= 25 for user in users)

        # 年齢範囲フィルター
        users, total = populated_repository.find_all(min_age=25, max_age=30)
        assert all(25 <= user.age <= 30 for user in users)

    @pytest.mark.unit
    def test_find_all_pagination(self, populated_repository: InMemoryUserRepository) -> None:
        """ページネーションテスト"""
        # 最初の2件
        users, total = populated_repository.find_all(limit=2, offset=0)
        assert len(users) == 2
        assert total == 5

        # 次の2件
        users, total = populated_repository.find_all(limit=2, offset=2)
        assert len(users) == 2
        assert total == 5

        # 最後の1件
        users, total = populated_repository.find_all(limit=2, offset=4)
        assert len(users) == 1
        assert total == 5

    @pytest.mark.unit
    def test_update(self, test_user_repository: InMemoryUserRepository) -> None:
        """ユーザー更新テスト"""
        user = test_user_repository.create(name="テストユーザー", email="test@example.com", age=25)
        original_updated_at = user.updated_at

        # 少し待機してから更新
        import time

        time.sleep(0.01)

        updated_user = test_user_repository.update(user.id, name="更新後ユーザー", age=30)

        assert updated_user is not None
        assert updated_user.id == user.id
        assert updated_user.name == "更新後ユーザー"
        assert updated_user.email == "test@example.com"
        assert updated_user.age == 30
        assert updated_user.updated_at > original_updated_at

    @pytest.mark.unit
    def test_update_nonexistent_user(self, test_user_repository: InMemoryUserRepository) -> None:
        """存在しないユーザー更新テスト"""
        updated_user = test_user_repository.update(999, name="更新後ユーザー")

        assert updated_user is None

    @pytest.mark.unit
    def test_delete(self, test_user_repository: InMemoryUserRepository) -> None:
        """ユーザー削除テスト"""
        user = test_user_repository.create(name="テストユーザー", email="test@example.com", age=25)

        # 削除実行
        success = test_user_repository.delete(user.id)
        assert success is True

        # 削除後に取得できないことを確認
        deleted_user = test_user_repository.find_by_id(user.id)
        assert deleted_user is None

        assert len(test_user_repository._users) == 0

    @pytest.mark.unit
    def test_delete_nonexistent_user(self, test_user_repository: InMemoryUserRepository) -> None:
        """存在しないユーザー削除テスト"""
        success = test_user_repository.delete(999)

        assert success is False

    @pytest.mark.unit
    def test_clear_all(self, populated_repository: InMemoryUserRepository) -> None:
        """全データ削除テスト"""
        # データが存在することを確認
        assert len(populated_repository._users) == 5
        assert populated_repository._user_counter == 5

        # 全削除実行
        populated_repository.clear_all()

        # データが削除されたことを確認
        assert len(populated_repository._users) == 0
        assert populated_repository._user_counter == 0

    @pytest.mark.unit
    def test_thread_safety(self, test_user_repository: InMemoryUserRepository) -> None:
        """スレッドセーフティテスト"""
        import threading

        results = []

        def create(i: int) -> None:
            user = test_user_repository.create(name=f"ユーザー{i}", email=f"user{i}@example.com", age=20 + i)
            results.append(user.id)

        # 複数のスレッドで同時にユーザーを作成
        threads = []
        for i in range(10):
            thread = threading.Thread(target=create, args=(i,))
            threads.append(thread)
            thread.start()

        # すべてのスレッドの完了を待機
        for thread in threads:
            thread.join()

        # 結果確認
        assert len(results) == 10
        assert len(set(results)) == 10  # すべて異なるIDであることを確認
        assert len(test_user_repository._users) == 10
