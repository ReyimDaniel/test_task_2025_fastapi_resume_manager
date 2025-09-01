import hashlib
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.engine import Result
from app_v1.models.user import User
from app_v1.schemas.user import UserCreate, UserUpdate, UserUpdatePartial


async def get_users(session: AsyncSession) -> list[User]:
    stmt = select(User).order_by(User.id)
    result: Result = await session.execute(stmt)
    return list(result.scalars().all())


async def get_user_by_id(session: AsyncSession, user_id: int) -> User | None:
    return await session.get(User, user_id)


async def create_user(session: AsyncSession, user_in: UserCreate) -> User:
    hashed_password = hashlib.sha256(user_in.password.encode()).hexdigest()

    db_user = User(
        name=user_in.name,
        email=user_in.email,
        hashed_password=hashed_password,
    )
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    return db_user


async def update_user(session: AsyncSession, user: User, user_update: UserUpdate | UserUpdatePartial,
                      partial: bool = False) -> User:
    for key, value in user_update.model_dump(exclude_unset=partial).items():
        setattr(user, key, value)
    await session.commit()
    await session.refresh(user)
    return user


async def delete_user(session: AsyncSession, user: User) -> None:
    await session.delete(user)
    await session.commit()
