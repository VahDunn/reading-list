from datetime import datetime
from typing import List

from pydantic import BaseModel, Field

from reading_list.api.schemas.common import Page
from reading_list.db.models.item import ItemKind, ItemPriority, ItemStatus


class ItemBase(BaseModel):
    title: str = Field(...)
    kind: ItemKind
    status: ItemStatus = ItemStatus.planned
    priority: ItemPriority = ItemPriority.normal
    notes: str | None = None


class ItemCreate(ItemBase):
    """Модель для создания Item."""

    tag_ids: List[int] | None = None


class ItemUpdate(BaseModel):
    """Частичное обновление Item."""

    title: str | None = Field(default=None)
    kind: ItemKind | None = None
    status: ItemStatus | None = None
    priority: ItemPriority | None = None
    notes: str | None = None
    tag_ids: List[int] | None = None


class ItemOut(BaseModel):
    id: int
    user_id: int
    title: str
    kind: ItemKind
    status: ItemStatus
    priority: ItemPriority
    notes: str | None
    created_at: datetime
    updated_at: datetime
    tag_ids: List[int]

    model_config = {
        'from_attributes': True
    }


class ItemPage(Page[ItemOut]):
    """Конкретный класс для страницы Item."""


class ItemTagsRemove(BaseModel):
    tag_ids: list[int]
