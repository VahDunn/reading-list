from fastapi import HTTPException, status

from reading_list.api.schemas.user import UserCreate, UserOut, UserUpdate
from reading_list.db.models.user import UserORM
from reading_list.repositories.user import UserRepository
from reading_list.services.abstract_crud import AbstractCrudService


class UserService(
    AbstractCrudService[UserCreate, UserUpdate, UserOut, None],
):

    def __init__(self, repo: UserRepository, user_id: int):
        self.repo = repo

    async def get_by_id(self, obj_id: int) -> UserOut:
        user = await self.repo.get_by_id(obj_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='User not found',
            )
        return self._to_user_out(user)

    async def get(self, filters: None = None) -> list[UserOut]:
        users = await self.repo.get_all()
        return [self._to_user_out(user) for user in users]

    async def create(self, payload: UserCreate) -> UserOut:
        email = str(payload.email)
        existing = await self.repo.get_by_email(email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='User with this email already exists',
            )

        user = UserORM(
            email=email,
            display_name=payload.display_name,
        )
        await self.repo.add(user)
        await self.repo.commit()
        await self.repo.refresh(user)
        return self._to_user_out(user)

    async def update(self, obj_id: int, payload: UserUpdate) -> UserOut:
        user = await self.repo.get_by_id(obj_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='User not found',
            )

        user_data = payload.model_dump(exclude_unset=True)

        new_email = user_data.get('email')
        if new_email is not None:
            existing = await self.repo.get_by_email(new_email)
            if existing and existing.id != obj_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail='User with this email already exists',
                )

        for field, field_value in user_data.items():
            setattr(user, field, field_value)

        await self.repo.commit()
        await self.repo.refresh(user)
        return self._to_user_out(user)

    async def delete(self, obj_id: int) -> int:
        user = await self.repo.get_by_id(obj_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='User not found',
            )

        await self.repo.delete(user)
        await self.repo.commit()
        return obj_id

    @staticmethod
    def _to_user_out(user: UserORM) -> UserOut:
        return UserOut(
            id=user.id,
            email=user.email,
            display_name=user.display_name,
            created_at=user.created_at,
        )
