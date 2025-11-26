from datetime import datetime

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    display_name: str


class UserCreate(UserBase):
    """Создание пользователя."""
    email: EmailStr


class UserUpdate(BaseModel):
    """Частичное обновление пользователя."""
    email: EmailStr | None = None
    display_name: str | None = None


class UserOut(UserBase):
    id: int
    created_at: datetime
    email: str
    model_config = {
        'from_attributes': True,
    }
