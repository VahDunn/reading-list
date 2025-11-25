from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, Sequence, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession

TModel = TypeVar("TModel")


class AbstractCrudRepository(ABC, Generic[TModel]):
    """
    Базовый абстрактный репозиторий для CRUD-операций.
    Конкретные репозитории знают про конкретную ORM-модель и фильтры.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    @abstractmethod
    async def get_by_id(self, obj_id: int) -> TModel | None:
        """Получить объект по id (или None)."""
        raise NotImplementedError

    @abstractmethod
    async def add(self, obj: TModel) -> TModel:
        """
        Добавить модель в сессию.
        """
        raise NotImplementedError

    @abstractmethod
    async def delete(self, obj: TModel) -> None:
        """
        Удалить модель.
        """
        raise NotImplementedError


    async def commit(self) -> None:
        await self.db.commit()

    async def refresh(self, obj: TModel, *, attribute_names: list[str] | None = None) -> TModel:
        if attribute_names:
            await self.db.refresh(obj, attribute_names=attribute_names)
        else:
            await self.db.refresh(obj)
        return obj
