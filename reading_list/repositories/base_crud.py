from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession

TModel = TypeVar('TModel')


class BaseCrudRepository(ABC, Generic[TModel]):

    def __init__(self, db: AsyncSession):
        self.db = db

    @abstractmethod
    async def get_by_id(self, obj_id: int) -> TModel | None:
        raise NotImplementedError

    async def add(self, orm_model: TModel) -> TModel:
        self.db.add(orm_model)
        await self.db.flush()
        return orm_model

    async def delete(self, db_obj: TModel) -> None:
        await self.db.delete(db_obj)

    async def commit(self) -> None:
        await self.db.commit()

    async def refresh(
        self,
        db_obj: TModel,
        *,
        attribute_names: list[str] | None = None,
    ) -> TModel:
        if attribute_names:
            await self.db.refresh(db_obj, attribute_names=attribute_names)
        else:
            await self.db.refresh(db_obj)
        return db_obj
