from datetime import datetime
from typing import Any, Iterable, Sequence

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from reading_list.db.models.item import (ItemKind, ItemORM, ItemPriority,
                                    ItemStatus)
from reading_list.db.models.tag import  TagORM
from reading_list.repositories.base_crud import BaseCrudRepository


class ItemRepository(BaseCrudRepository[ItemORM]):
    def __init__(self, db: AsyncSession):
        super().__init__(db)

    async def get_by_id(self, obj_id: int) -> ItemORM | None:
        stmt = select(ItemORM).where(ItemORM.id == obj_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_item_for_user(
        self,
        item_id: int,
        user_id: int,
        with_tags: bool = False,
    ) -> ItemORM | None:
        stmt = select(ItemORM).where(
            ItemORM.id == item_id,
            ItemORM.user_id == user_id,
        )
        if with_tags:
            stmt = stmt.options(joinedload(ItemORM.tags))

        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_with_filters(
        self,
        *,
        user_id: int,
        status: ItemStatus | None = None,
        kind: ItemKind | None = None,
        priority: ItemPriority | None = None,
        tag_ids: Iterable[int] | None = None,
        q: str | None = None,
        created_from: datetime | None = None,
        created_to: datetime | None = None,
        limit: int = 20,
        offset: int = 0,
        sort_by: str = "created_at",
        sort_dir: str = "desc",
    ) -> tuple[list[ItemORM], int]:
        """
        Возвращает (items, total_count) с учётом фильтров, пагинации и сортировки.
        Фильтр по тегам — "любая из" (OR).
        """

        base_stmt = select(ItemORM).where(ItemORM.user_id == user_id)
        count_stmt = select(func.count(func.distinct(ItemORM.id))).where(ItemORM.user_id == user_id)

        conditions: list[Any] = []

        simple_filters: list[tuple[Any | None, Any]] = [
            (status, ItemORM.status),
            (kind, ItemORM.kind),
            (priority, ItemORM.priority),
        ]
        for value, column in simple_filters:
            if value is not None:
                conditions.append(column == value)

        if q:
            conditions.append(ItemORM.title.ilike(f"%{q}%"))

        if created_from is not None:
            conditions.append(ItemORM.created_at >= created_from)

        if created_to is not None:
            conditions.append(ItemORM.created_at <= created_to)

        if tag_ids:
            base_stmt = base_stmt.join(ItemORM.tags)
            count_stmt = count_stmt.join(ItemORM.tags)
            conditions.append(TagORM.id.in_(list(tag_ids)))
            base_stmt = base_stmt.distinct()

        if conditions:
            cond = and_(*conditions)
            base_stmt = base_stmt.where(cond)
            count_stmt = count_stmt.where(cond)

        sort_column_map = {
            "created_at": ItemORM.created_at,
            "updated_at": ItemORM.updated_at,
            "priority": ItemORM.priority,
        }
        sort_col = sort_column_map.get(sort_by, ItemORM.created_at)
        if sort_dir == "asc":
            base_stmt = base_stmt.order_by(sort_col.asc())
        else:
            base_stmt = base_stmt.order_by(sort_col.desc())

        base_stmt = base_stmt.offset(offset).limit(limit)
        base_stmt = base_stmt.options(joinedload(ItemORM.tags))

        items_result = await self.db.execute(base_stmt)
        items = list(items_result.unique().scalars().all())

        total_result = await self.db.execute(count_stmt)
        total = total_result.scalar_one()

        return items, total

    async def get_tags_for_user_by_ids(
        self,
        user_id: int,
        tag_ids: list[int],
    ) -> Sequence[TagORM]:
        if not tag_ids:
            return []

        stmt = select(TagORM).where(
            TagORM.user_id == user_id,
            TagORM.id.in_(tag_ids),
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
