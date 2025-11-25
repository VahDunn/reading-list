from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, Sequence, TypeVar

CreateSchema = TypeVar("CreateSchema")
UpdateSchema = TypeVar("UpdateSchema")
ReadSchema = TypeVar("ReadSchema")
FiltersSchema = TypeVar("FiltersSchema")


class AbstractCrudService(
    ABC,
    Generic[
        CreateSchema,
        UpdateSchema,
        ReadSchema,
        FiltersSchema,
    ],
):

    @abstractmethod
    async def get_by_id(self, obj_id: int) -> ReadSchema:
        ...

    @abstractmethod
    async def get(self, filters: FiltersSchema | None = None):
        ...

    @abstractmethod
    async def create(self, payload: CreateSchema) -> ReadSchema:
        ...

    @abstractmethod
    async def update(self, obj_id: int, payload: UpdateSchema) -> ReadSchema:
        ...

    @abstractmethod
    async def delete(self, obj_id: int) -> int:
        ...
