from fastapi import APIRouter, status, Depends, Query
from backend.database import SessionDep
from backend.schemas.user import UserResponse, UserUpdate
from backend.services.user import get_user_by_id, get_users_list, update_user, delete_user
from backend.utils.security import get_current_user
from backend.models.user import User

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.get("/", response_model=list[UserResponse])
async def list_users(
    db: SessionDep,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    users = await get_users_list(db, skip=skip, limit=limit)
    return users


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: SessionDep):
    user = await get_user_by_id(db, user_id)
    if not user:
        from backend.utils.exceptions import UserNotFoundError
        raise UserNotFoundError(identifier=f"user_id={user_id}")
    return user


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user_profile(
    user_id: int,
    data: UserUpdate,
    db: SessionDep,
    current_user: User = Depends(get_current_user),
):
    if current_user.id != user_id:
        from backend.utils.exceptions import PermissionDeniedError
        raise PermissionDeniedError(detail="You can only update your own profile")

    user = await update_user(db, user_id, data)
    if not user:
        from backend.utils.exceptions import UserNotFoundError
        raise UserNotFoundError(identifier=f"user_id={user_id}")
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_user(
    user_id: int,
    db: SessionDep,
    current_user: User = Depends(get_current_user),
):
    if current_user.id != user_id:
        from backend.utils.exceptions import PermissionDeniedError
        raise PermissionDeniedError(detail="You can only deactivate your own account")

    result = await delete_user(db, user_id)
    if not result:
        from backend.utils.exceptions import UserNotFoundError
        raise UserNotFoundError(identifier=f"user_id={user_id}")
