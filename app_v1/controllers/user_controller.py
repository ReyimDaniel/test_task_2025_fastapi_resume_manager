from typing import Annotated

from fastapi import APIRouter, Depends, Path, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app_v1.schemas.user import User
from app_v1.core import db_helper
from app_v1.repositories import user_repository
from app_v1.schemas.user import UserRead, UserCreate, UserUpdate, UserUpdatePartial

router = APIRouter(tags=['users'])


@router.get('/', response_model=list[User])
async def get_users(session: AsyncSession = Depends(db_helper.scoped_session_dependency)):
    return await user_repository.get_users(session=session)


@router.post('/', response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(user_in: UserCreate,
                      session: AsyncSession = Depends(db_helper.scoped_session_dependency)):
    return await user_repository.create_user(session=session, user_in=user_in)


async def get_user_by_id(user_id: Annotated[int, Path],
                         session: AsyncSession = Depends(db_helper.scoped_session_dependency)) -> User:
    user = await user_repository.get_user_by_id(session=session, user_id=user_id)
    if user is not None:
        return user
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User {user_id} not found")


@router.get('/{user_id}', response_model=User)
async def get_user(user: User = Depends(get_user_by_id)):
    return user


@router.put('/{user_id}', response_model=User)
async def update_user(user_update: UserUpdate,
                      user: User = Depends(get_user_by_id),
                      session: AsyncSession = Depends(db_helper.scoped_session_dependency)):
    return await user_repository.update_user(session=session, user=user, user_update=user_update)


@router.patch("/{user_id}", response_model=User)
async def update_user_partial(user_update: UserUpdatePartial,
                              user: User = Depends(get_user_by_id),
                              session: AsyncSession = Depends(db_helper.scoped_session_dependency)):
    return await user_repository.update_user(session=session, user=user, user_update=user_update, partial=True)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user: User = Depends(get_user_by_id),
                      session: AsyncSession = Depends(db_helper.scoped_session_dependency)):
    return await user_repository.delete_user(session=session, user=user)
