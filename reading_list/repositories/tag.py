from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from reading_list.db.models.tag import TagORM
from reading_list.repositories.base_crud import BaseCrudRepository


class TagRepository(BaseCrudRepository[TagORM]):
    def __init__(self, db: AsyncSession):
        super().__init__(db)

    async def get_by_id(self, obj_id: int) -> TagORM | None:
        stmt = select(TagORM).where(TagORM.id == obj_id)
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def get_for_user(self, user_id: int) -> Sequence[TagORM]:
        stmt = (
            select(TagORM)
           .where(TagORM.user_id == user_id)
            .order_by(TagORM.name.asc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_name_for_user(
            self, user_id: int, name: str
    ) -> TagORM | None:
        stmt = select(TagORM).where(
            TagORM.user_id == user_id,
            TagORM.name == name,
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
