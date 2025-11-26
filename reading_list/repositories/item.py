from typing import Any, Sequence

from sqlalchemy import Select, and_, func, select
from sqlalchemy.orm import joinedload

from reading_list.api.schemas.item_filter import ItemFilter
from reading_list.db.models.item import ItemORM
from reading_list.db.models.tag import TagORM
from reading_list.repositories.base_crud import BaseCrudRepository


class ItemRepository(BaseCrudRepository[ItemORM]):

    async def get_by_id(self, obj_id: int) -> ItemORM | None:
        stmt = select(ItemORM).where(ItemORM.id == obj_id)
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

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

        res = await self.db.execute(stmt)
        return res.unique().scalar_one_or_none()

    async def get_with_filters(
        self,
        user_id: int,
        filters: ItemFilter,
    ) -> tuple[list[ItemORM], int]:
        base_stmt, count_stmt = self._build_base_queries(user_id)
        base_stmt, count_stmt = self._apply_filters(
            base_stmt, count_stmt, filters
        )
        base_stmt = self._apply_sorting(base_stmt, filters)
        base_stmt = self._apply_pagination_and_options(base_stmt, filters)
        items_result = await self.db.execute(base_stmt)
        db_items = list(items_result.unique().scalars().all())
        total = (await self.db.execute(count_stmt)).scalar_one()
        return db_items, total

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
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    @staticmethod
    def _build_base_queries(
        user_id: int,
    ) -> tuple[Select, Select]:
        base_stmt = select(ItemORM).where(ItemORM.user_id == user_id)
        count_stmt = select(
            func.count(func.distinct(ItemORM.id)),
        ).where(ItemORM.user_id == user_id)
        return base_stmt, count_stmt

    @staticmethod
    def _apply_filters(   # noqa: WPS210
        base_stmt: Select,
        count_stmt: Select,
        filters: ItemFilter,
    ) -> tuple[Select, Select]:
        conditions: list[Any] = []

        filter_pairs = (
            (filters.status, ItemORM.status),
            (filters.kind, ItemORM.kind),
            (filters.priority, ItemORM.priority),
        )

        for filter_val, col in filter_pairs:
            if filter_val is not None:
                conditions.append(col == filter_val)

        if filters.q:
            conditions.append(ItemORM.title.ilike(f'%{filters.q}%'))

        if filters.created_from is not None:
            conditions.append(ItemORM.created_at >= filters.created_from)

        if filters.created_to is not None:
            conditions.append(ItemORM.created_at <= filters.created_to)

        tag_ids = filters.tag_ids or []
        if tag_ids:
            base_stmt = base_stmt.join(ItemORM.tags)
            count_stmt = count_stmt.join(ItemORM.tags)
            conditions.append(TagORM.id.in_(tag_ids))
            base_stmt = base_stmt.distinct()

        if conditions:
            cond = and_(*conditions)
            base_stmt = base_stmt.where(cond)
            count_stmt = count_stmt.where(cond)

        return base_stmt, count_stmt

    @staticmethod
    def _apply_sorting(
        stmt: Select,
        filters: ItemFilter,
    ) -> Select:
        sort_column_map = {
            'created_at': ItemORM.created_at,
            'updated_at': ItemORM.updated_at,
            'priority': ItemORM.priority,
        }

        sort_by = filters.sort_by or 'created_at'
        sort_dir = filters.sort_dir or 'desc'

        sort_col = sort_column_map.get(sort_by, ItemORM.created_at)

        if sort_dir == 'asc':
            return stmt.order_by(sort_col.asc())
        return stmt.order_by(sort_col.desc())

    @staticmethod
    def _apply_pagination_and_options(
        stmt: Select,
        filters: ItemFilter,
    ) -> Select:
        return (
            stmt.offset(
                filters.offset
            ).limit(
                filters.limit
            ).options(
                joinedload(ItemORM.tags)
            )
        )
