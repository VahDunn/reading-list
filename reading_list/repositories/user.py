from typing import Sequence

from sqlalchemy import select

from reading_list.db.models.user import UserORM
from reading_list.repositories.base_crud import BaseCrudRepository


class UserRepository(BaseCrudRepository[UserORM]):

    async def get_by_id(self, obj_id: int) -> UserORM | None:
        stmt = select(UserORM).where(UserORM.id == obj_id)
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def get_all(self) -> Sequence[UserORM]:
        stmt = select(UserORM)
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def get_by_email(self, email: str) -> UserORM | None:
        stmt = select(UserORM).where(UserORM.email == email)
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()
