from pydantic import BaseModel, EmailStr, ConfigDict


class UserBase(BaseModel):
    name: str
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserRead(UserBase):
    id: int
    email: EmailStr

    class Config:
        from_attributes = True


class UserUpdate(UserBase):
    password: str | None = None


class UserUpdatePartial(UserBase):
    name: str | None = None
    email: EmailStr | None = None
    password: str | None = None


class User(UserBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
