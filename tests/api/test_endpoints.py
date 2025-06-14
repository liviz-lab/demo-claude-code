import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient


class TestHealthEndpoint:
    """ヘルスチェックエンドポイントのテスト"""

    @pytest.mark.api
    def test_health_check_success(self, client: TestClient) -> None:
        """ヘルスチェック成功テスト"""
        response = client.get("/api/v1/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "message" in data


class TestUserEndpoints:
    """ユーザー関連エンドポイントのテスト"""

    @pytest.mark.api
    def test_get_users_empty(self, client: TestClient, auth_headers: dict[str, str]) -> None:
        """空のユーザーリスト取得テスト"""
        response = client.get("/api/v1/users", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["users"] == []
        assert data["total"] == 0
        assert data["limit"] == 10
        assert data["offset"] == 0

    @pytest.mark.api
    def test_get_users_without_auth(self, client: TestClient) -> None:
        """認証なしでユーザーリスト取得テスト"""
        response = client.get("/api/v1/users")

        assert response.status_code == 401
        data = response.json()
        assert data["code"] == "missing_api_key"

    @pytest.mark.api
    def test_get_users_invalid_auth(self, client: TestClient, invalid_auth_headers: dict[str, str]) -> None:
        """無効な認証でユーザーリスト取得テスト"""
        response = client.get("/api/v1/users", headers=invalid_auth_headers)

        assert response.status_code == 401
        data = response.json()
        assert data["code"] == "invalid_api_key"

    @pytest.mark.api
    def test_create_user_success(self, client: TestClient, auth_headers: dict[str, str], sample_user_data: dict[str, str | int]) -> None:
        """ユーザー作成成功テスト"""
        response = client.post("/api/v1/users", json=sample_user_data, headers=auth_headers)

        assert response.status_code == 201
        data = response.json()
        assert data["message"] == "ユーザーが正常に作成されました"
        assert data["user"]["name"] == sample_user_data["name"]
        assert data["user"]["email"] == sample_user_data["email"]
        assert data["user"]["age"] == sample_user_data["age"]
        assert "id" in data["user"]
        assert "created_at" in data["user"]
        assert "updated_at" in data["user"]

    @pytest.mark.api
    def test_create_user_validation_error(self, client: TestClient, auth_headers: dict[str, str]) -> None:
        """ユーザー作成バリデーションエラーテスト"""
        invalid_data = {
            "name": "",  # 空文字
            "email": "invalid-email",  # 無効なメール
            "age": -1,  # 無効な年齢
        }

        response = client.post("/api/v1/users", json=invalid_data, headers=auth_headers)

        assert response.status_code == 422
        data = response.json()
        assert data["code"] == "VAL_001"
        assert "details" in data

    @pytest.mark.api
    def test_create_user_duplicate_email(self, client: TestClient, auth_headers: dict[str, str], sample_user_data: dict[str, str | int]) -> None:
        """重複メールアドレスでユーザー作成テスト"""
        # 最初のユーザーを作成
        client.post("/api/v1/users", json=sample_user_data, headers=auth_headers)

        # 同じメールアドレスで再度作成
        response = client.post("/api/v1/users", json=sample_user_data, headers=auth_headers)

        assert response.status_code == 422
        data = response.json()
        assert data["code"] == "VAL_002"
        assert "既に使用されています" in data["message"]

    @pytest.mark.api
    def test_get_user_by_id_success(self, client: TestClient, auth_headers: dict[str, str], sample_user_data: dict[str, str | int]) -> None:
        """ユーザーID取得成功テスト"""
        # ユーザー作成
        create_response = client.post("/api/v1/users", json=sample_user_data, headers=auth_headers)
        user_id = create_response.json()["user"]["id"]

        # ユーザー取得
        response = client.get(f"/api/v1/users/{user_id}", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == user_id
        assert data["name"] == sample_user_data["name"]
        assert data["email"] == sample_user_data["email"]
        assert data["age"] == sample_user_data["age"]

    @pytest.mark.api
    def test_get_user_by_id_not_found(self, client: TestClient, auth_headers: dict[str, str]) -> None:
        """存在しないユーザーID取得テスト"""
        response = client.get("/api/v1/users/999", headers=auth_headers)

        assert response.status_code == 404
        data = response.json()
        assert data["code"] == "RES_002"
        assert "見つかりません" in data["message"]

    @pytest.mark.api
    def test_update_user_success(self, client: TestClient, auth_headers: dict[str, str], sample_user_data: dict[str, str | int]) -> None:
        """ユーザー更新成功テスト"""
        # ユーザー作成
        create_response = client.post("/api/v1/users", json=sample_user_data, headers=auth_headers)
        user_id = create_response.json()["user"]["id"]

        # ユーザー更新
        update_data = {"name": "更新後ユーザー", "age": 30}
        response = client.put(f"/api/v1/users/{user_id}", json=update_data, headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "ユーザーが正常に更新されました"
        assert data["user"]["name"] == update_data["name"]
        assert data["user"]["age"] == update_data["age"]
        assert data["user"]["email"] == sample_user_data["email"]  # 変更されていない

    @pytest.mark.api
    def test_update_user_not_found(self, client: TestClient, auth_headers: dict[str, str]) -> None:
        """存在しないユーザー更新テスト"""
        update_data = {"name": "更新後ユーザー"}
        response = client.put("/api/v1/users/999", json=update_data, headers=auth_headers)

        assert response.status_code == 404
        data = response.json()
        assert data["code"] == "RES_002"

    @pytest.mark.api
    def test_delete_user_success(self, client: TestClient, auth_headers: dict[str, str], sample_user_data: dict[str, str | int]) -> None:
        """ユーザー削除成功テスト"""
        # ユーザー作成
        create_response = client.post("/api/v1/users", json=sample_user_data, headers=auth_headers)
        user_id = create_response.json()["user"]["id"]

        # ユーザー削除
        response = client.delete(f"/api/v1/users/{user_id}", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "ユーザーが正常に削除されました"
        assert data["deleted_user_id"] == user_id

        # 削除後に取得できないことを確認
        get_response = client.get(f"/api/v1/users/{user_id}", headers=auth_headers)
        assert get_response.status_code == 404

    @pytest.mark.api
    def test_delete_user_not_found(self, client: TestClient, auth_headers: dict[str, str]) -> None:
        """存在しないユーザー削除テスト"""
        response = client.delete("/api/v1/users/999", headers=auth_headers)

        assert response.status_code == 404
        data = response.json()
        assert data["code"] == "RES_002"

    @pytest.mark.api
    def test_get_users_with_filters(self, client: TestClient, auth_headers: dict[str, str]) -> None:
        """フィルター付きユーザーリスト取得テスト"""
        # テストユーザーを複数作成
        users_data = [
            {"name": "田中太郎", "email": "tanaka@example.com", "age": 30},
            {"name": "佐藤花子", "email": "sato@example.com", "age": 25},
            {"name": "田中次郎", "email": "tanaka2@example.com", "age": 35},
        ]

        for user_data in users_data:
            client.post("/api/v1/users", json=user_data, headers=auth_headers)

        # 名前でフィルター
        response = client.get("/api/v1/users?name=田中", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2

        # 年齢でフィルター
        response = client.get("/api/v1/users?min_age=30", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2

        # ページネーション
        response = client.get("/api/v1/users?limit=2&offset=1", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["users"]) == 2
        assert data["limit"] == 2
        assert data["offset"] == 1


class TestRootEndpoint:
    """ルートエンドポイントのテスト"""

    @pytest.mark.api
    def test_root_endpoint(self, client: TestClient) -> None:
        """ルートエンドポイントテスト"""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "docs" in data
        assert "health" in data


@pytest.mark.asyncio
class TestAsyncEndpoints:
    """非同期エンドポイントのテスト"""

    @pytest.mark.api
    async def test_async_create_user(self, async_client: AsyncClient, auth_headers: dict[str, str], sample_user_data: dict[str, str | int]) -> None:
        """非同期でのユーザー作成テスト"""
        response = await async_client.post("/api/v1/users", json=sample_user_data, headers=auth_headers)

        assert response.status_code == 201
        data = response.json()
        assert data["message"] == "ユーザーが正常に作成されました"
        assert data["user"]["name"] == sample_user_data["name"]

    @pytest.mark.api
    async def test_async_get_users(self, async_client: AsyncClient, auth_headers: dict[str, str]) -> None:
        """非同期でのユーザーリスト取得テスト"""
        response = await async_client.get("/api/v1/users", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "users" in data
        assert "total" in data
