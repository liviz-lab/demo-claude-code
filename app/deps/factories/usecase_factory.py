from fastapi import Depends

from app.deps.factories.repository_factory import get_user_repository
from app.ports.user_repository import UserRepository
from app.usecase.command.create_user import CreateUserUseCase
from app.usecase.command.delete_user import DeleteUserUseCase
from app.usecase.command.update_user import UpdateUserUseCase
from app.usecase.query.get_user import GetUserUseCase
from app.usecase.query.get_users import GetUsersUseCase


def get_get_users_usecase(user_repository: UserRepository = Depends(get_user_repository)) -> GetUsersUseCase:
    """ユーザーリスト取得ユースケースの依存性注入"""
    return GetUsersUseCase(user_repository)


def get_get_user_usecase(user_repository: UserRepository = Depends(get_user_repository)) -> GetUserUseCase:
    """ユーザー詳細取得ユースケースの依存性注入"""
    return GetUserUseCase(user_repository)


def get_create_user_usecase(user_repository: UserRepository = Depends(get_user_repository)) -> CreateUserUseCase:
    """ユーザー作成ユースケースの依存性注入"""
    return CreateUserUseCase(user_repository)


def get_update_user_usecase(user_repository: UserRepository = Depends(get_user_repository)) -> UpdateUserUseCase:
    """ユーザー更新ユースケースの依存性注入"""
    return UpdateUserUseCase(user_repository)


def get_delete_user_usecase(user_repository: UserRepository = Depends(get_user_repository)) -> DeleteUserUseCase:
    """ユーザー削除ユースケースの依存性注入"""
    return DeleteUserUseCase(user_repository)
