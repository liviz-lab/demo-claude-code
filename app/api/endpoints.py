from typing import Annotated

from fastapi import APIRouter, Depends, Path

from app.deps.factories.usecase_factory import (
    get_create_user_usecase,
    get_delete_user_usecase,
    get_get_user_usecase,
    get_get_users_usecase,
    get_update_user_usecase,
)
from app.usecase.command.create_user import CreateUserUseCase
from app.usecase.command.delete_user import DeleteUserUseCase
from app.usecase.command.update_user import UpdateUserUseCase
from app.usecase.query.get_user import GetUserUseCase
from app.usecase.query.get_users import GetUsersUseCase
from schemas.requests import UserCreateRequest, UsersQuery, UserUpdateRequest
from schemas.responses import (
    UserCreateResponse,
    UserDeleteResponse,
    UserListResponse,
    UserResponse,
    UserUpdateResponse,
)

router = APIRouter()


@router.get("/users", response_model=UserListResponse, summary="ユーザーリスト取得")
async def get_users(
    query: Annotated[UsersQuery, Depends()],
    usecase: Annotated[GetUsersUseCase, Depends(get_get_users_usecase)],
) -> UserListResponse:
    """
    ユーザーリストを取得します。

    - **name**: 名前で部分一致検索
    - **min_age**: 最小年齢でフィルタ
    - **max_age**: 最大年齢でフィルタ
    - **limit**: 取得件数（1-100）
    - **offset**: オフセット（ページネーション用）
    """
    users, total = usecase.execute(query)

    # エンティティからレスポンスに変換
    user_responses = [
        UserResponse(
            id=user.id,
            name=user.name,
            email=user.email,
            age=user.age,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )
        for user in users
    ]

    return UserListResponse(users=user_responses, total=total, limit=query.limit, offset=query.offset)


@router.get("/users/{user_id}", response_model=UserResponse, summary="ユーザー詳細取得")
async def get_user(
    usecase: Annotated[GetUserUseCase, Depends(get_get_user_usecase)],
    user_id: int = Path(..., ge=1, description="ユーザーID"),
) -> UserResponse:
    """
    指定されたIDのユーザー詳細情報を取得します。

    - **user_id**: 取得するユーザーのID
    """
    user = usecase.execute(user_id)

    return UserResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        age=user.age,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


@router.post("/users", response_model=UserCreateResponse, summary="ユーザー作成", status_code=201)
async def create_user(
    request: UserCreateRequest,
    usecase: Annotated[CreateUserUseCase, Depends(get_create_user_usecase)],
) -> UserCreateResponse:
    """
    新しいユーザーを作成します。

    - **name**: ユーザー名（1-100文字）
    - **email**: メールアドレス（有効な形式）
    - **age**: 年齢（0-120）
    """
    user = usecase.execute(request)

    user_response = UserResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        age=user.age,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )

    return UserCreateResponse(message="ユーザーが正常に作成されました", user=user_response)


@router.put("/users/{user_id}", response_model=UserUpdateResponse, summary="ユーザー更新")
async def update_user(
    request: UserUpdateRequest,
    usecase: Annotated[UpdateUserUseCase, Depends(get_update_user_usecase)],
    user_id: int = Path(..., ge=1, description="ユーザーID"),
) -> UserUpdateResponse:
    """
    指定されたIDのユーザー情報を更新します。

    - **user_id**: 更新するユーザーのID
    - **name**: ユーザー名（1-100文字）※省略可
    - **email**: メールアドレス（有効な形式）※省略可
    - **age**: 年齢（0-120）※省略可
    """
    user = usecase.execute(user_id, request)

    user_response = UserResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        age=user.age,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )

    return UserUpdateResponse(message="ユーザーが正常に更新されました", user=user_response)


@router.delete("/users/{user_id}", response_model=UserDeleteResponse, summary="ユーザー削除")
async def delete_user(
    usecase: Annotated[DeleteUserUseCase, Depends(get_delete_user_usecase)],
    user_id: int = Path(..., ge=1, description="ユーザーID"),
) -> UserDeleteResponse:
    """
    指定されたIDのユーザーを削除します。

    - **user_id**: 削除するユーザーのID
    """
    deleted_user_id = usecase.execute(user_id)

    return UserDeleteResponse(message="ユーザーが正常に削除されました", deleted_user_id=deleted_user_id)


@router.get("/health", summary="ヘルスチェック")
async def health_check() -> dict[str, str]:
    """
    API の動作確認用のヘルスチェックエンドポイント。
    認証不要。
    """
    return {"status": "healthy", "message": "API is running successfully"}
