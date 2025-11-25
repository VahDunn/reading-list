from fastapi import HTTPException, status

from reading_list.api.schemas.common import PageMeta
from reading_list.api.schemas.item import (ItemCreate, ItemOut, ItemPage,
                                                ItemUpdate)
from reading_list.api.schemas.item_filters import ItemFilters
from reading_list.db.models.item import ItemORM
from reading_list.repositories.item import ItemRepository
from reading_list.services.abstract_crud import AbstractCrudService


class ItemsService(AbstractCrudService[ItemCreate, ItemUpdate, ItemOut, ItemFilters]):
    def __init__(self, repo: ItemRepository, user_id: int):
        self.repo = repo
        self.user_id = user_id

    async def _apply_tags_by_ids(
        self,
        item: ItemORM,
        tag_ids: list[int] | None,
    ) -> None:
        if tag_ids is None:
            return

        if not tag_ids:
            item.tags = []
            return

        tags = await self.repo.get_tags_for_user_by_ids(self.user_id, tag_ids)
        found_ids = {t.id for t in tags}
        missing = set(tag_ids) - found_ids
        if missing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Tags not found or do not belong to user: {sorted(missing)}",
            )

        item.tags = list(tags)

    def _to_item_out(self, item: ItemORM) -> ItemOut:
        return ItemOut(
            id=item.id,
            user_id=item.user_id,
            title=item.title,
            kind=item.kind,
            status=item.status,
            priority=item.priority,
            notes=item.notes,
            created_at=item.created_at,
            updated_at=item.updated_at,
            tag_ids=[t.id for t in item.tags],
        )

    async def get_by_id(self, obj_id: int) -> ItemOut:
        item = await self.repo.get_item_for_user(
            item_id=obj_id,
            user_id=self.user_id,
            with_tags=True,
        )
        if item is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item not found",
            )
        return self._to_item_out(item)

    async def get(self, filters: ItemFilters | None = None) -> ItemPage:
        data = filters.model_dump(exclude_none=True) if filters else {}
        items, total = await self.repo.get_with_filters(
            user_id=self.user_id,
            **data,
        )
        return ItemPage(
            items_list=[self._to_item_out(i) for i in items],
            meta=PageMeta(total=total, limit=filters.limit, offset=filters.offset),
        )

    async def create(self, payload: ItemCreate) -> ItemOut:
        item = ItemORM(
            user_id=self.user_id,
            title=payload.title,
            kind=payload.kind,
            status=payload.status,
            priority=payload.priority,
            notes=payload.notes,
        )

        await self._apply_tags_by_ids(item, payload.tag_ids)

        await self.repo.add(item)
        await self.repo.commit()
        await self.repo.refresh(item, attribute_names=["tags"])

        return self._to_item_out(item)

    async def update(self, obj_id: int, payload: ItemUpdate) -> ItemOut:
        item = await self.repo.get_item_for_user(
            item_id=obj_id,
            user_id=self.user_id,
            with_tags=True,
        )
        if item is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item not found",
            )

        data = payload.model_dump(exclude_unset=True)
        tag_ids = data.pop("tag_ids", None)

        for field, value in data.items_list():
            setattr(item, field, value)

        await self._apply_tags_by_ids(item, tag_ids)

        await self.repo.commit()
        await self.repo.refresh(item, attribute_names=["tags"])

        return self._to_item_out(item)

    async def delete(self, obj_id: int) -> int:
        item = await self.repo.get_item_for_user(
            item_id=obj_id,
            user_id=self.user_id,
        )
        if item is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item not found",
            )

        await self.repo.delete(item)
        await self.repo.commit()
        return obj_id
