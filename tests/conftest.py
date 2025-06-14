import asyncio
from collections.abc import AsyncGenerator, Generator

import httpx
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient

from app.core.config import settings
from app.deps.factories.repository_factory import get_user_repository
from app.infra.user_repository_impl import InMemoryUserRepository
from main import app


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """イベントループを作成（セッションスコープ）"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_user_repository() -> InMemoryUserRepository:
    """テスト用のクリーンなユーザーリポジトリインスタンスを提供"""
    repo = InMemoryUserRepository()
    return repo


@pytest.fixture
def client(test_user_repository: InMemoryUserRepository) -> Generator[TestClient, None, None]:
    """テスト用クライアント（同期版）"""

    def get_test_user_repository() -> InMemoryUserRepository:
        return test_user_repository

    app.dependency_overrides[get_user_repository] = get_test_user_repository

    with TestClient(app) as test_client:
        yield test_client

    # クリーンアップ
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def async_client(test_user_repository: InMemoryUserRepository) -> AsyncGenerator[AsyncClient, None]:
    """テスト用クライアント（非同期版）"""

    def get_test_user_repository() -> InMemoryUserRepository:
        return test_user_repository

    app.dependency_overrides[get_user_repository] = get_test_user_repository

    async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

    # クリーンアップ
    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers() -> dict[str, str]:
    """認証ヘッダーを提供"""
    return {settings.AUTH_HEADER_NAME: settings.AUTH_HEADER_VALUE}


@pytest.fixture
def invalid_auth_headers() -> dict[str, str]:
    """無効な認証ヘッダーを提供"""
    return {settings.AUTH_HEADER_NAME: "invalid-key"}


@pytest.fixture
def sample_user_data() -> dict[str, str | int]:
    """サンプルユーザーデータ"""
    return {"name": "テストユーザー", "email": "test@example.com", "age": 25}


@pytest.fixture
def sample_users_data() -> list[dict[str, str | int]]:
    """複数のサンプルユーザーデータ"""
    return [
        {"name": "田中太郎", "email": "tanaka@example.com", "age": 30},
        {"name": "佐藤花子", "email": "sato@example.com", "age": 25},
        {"name": "高橋次郎", "email": "takahashi@example.com", "age": 35},
        {"name": "山田美咲", "email": "yamada@example.com", "age": 28},
        {"name": "小林健太", "email": "kobayashi@example.com", "age": 22},
    ]


@pytest.fixture
def populated_repository(
    test_user_repository: InMemoryUserRepository, sample_users_data: list[dict[str, str | int]]
) -> InMemoryUserRepository:
    """サンプルデータが入ったリポジトリ"""
    for user_data in sample_users_data:
        test_user_repository.create(**user_data)
    return test_user_repository
