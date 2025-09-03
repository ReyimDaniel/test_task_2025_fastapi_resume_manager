from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.app_v1.core import db_helper
from app.app_v1.models import User
from app.app_v1.schemas.user import UserCreate
from app.app_v1.auth.model.token_model import Token
from app.app_v1.auth.service.jwt_service import create_access_token, get_password_hash, verify_password

router = APIRouter(tags=["JWT Auth"])


@router.post("/register")
async def register(user: UserCreate, session: AsyncSession = Depends(db_helper.get_scoped_session)):
    result = await session.execute(select(User).where(User.email == user.email))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(name=user.name, email=user.email, password=get_password_hash(user.password))
    session.add(new_user)
    await session.commit()
    return {"msg": "User registered successfully"}


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(),
                session: AsyncSession = Depends(db_helper.get_scoped_session)):
    result = await session.execute(select(User).where(User.email == form_data.username))
    db_user = result.scalars().first()
    if not db_user or not verify_password(form_data.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": db_user.email})
    return {"access_token": token, "token_type": "bearer"}
