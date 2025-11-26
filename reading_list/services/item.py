from fastapi import HTTPException, status

from reading_list.api.schemas.common import PageMeta
from reading_list.api.schemas.item import ItemCreate, ItemOut, ItemPage, ItemUpdate
from reading_list.api.schemas.item_filter import ItemFilter
from reading_list.db.models.item import ItemORM
from reading_list.repositories.item import ItemRepository
from reading_list.services.abstract_crud import AbstractCrudService


class ItemsService(
    AbstractCrudService[ItemCreate, ItemUpdate, ItemOut, ItemFilter]
):
    def __init__(self, repo: ItemRepository, user_id: int):
        self.repo = repo
        self.user_id = user_id
        self.not_found_msg = 'Item not found'

    async def get_by_id(self, obj_id: int) -> ItemOut:
        db_item = await self.repo.get_item_for_user(
            item_id=obj_id,
            user_id=self.user_id,
            with_tags=True,
        )
        if db_item is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=self.not_found_msg,
            )
        return self._to_item_out(db_item)

    async def get(self, filters: ItemFilter | None = None) -> ItemPage:
        filters = filters or ItemFilter()
        db_items, total = await self.repo.get_with_filters(
            user_id=self.user_id,
            filters=filters,
        )
        return ItemPage(
            items_list=[self._to_item_out(db_item) for db_item in db_items],
            meta=PageMeta(
                total=total,
                limit=filters.limit,
                offset=filters.offset,
            ),
        )

    async def create(self, payload: ItemCreate) -> ItemOut:
        item_for_db = ItemORM(
            user_id=self.user_id,
            title=payload.title,
            kind=payload.kind,
            status=payload.status,
            priority=payload.priority,
            notes=payload.notes,
        )

        await self._apply_tags_by_ids(item_for_db, payload.tag_ids)

        await self.repo.add(item_for_db)
        await self.repo.commit()
        await self.repo.refresh(item_for_db, attribute_names=['tags'])

        return self._to_item_out(item_for_db)

    async def update(self, obj_id: int, payload: ItemUpdate) -> ItemOut:
        db_item = await self.repo.get_item_for_user(
            item_id=obj_id,
            user_id=self.user_id,
            with_tags=True,
        )
        if db_item is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=self.not_found_msg,
            )

        payload_dict = payload.model_dump(exclude_unset=True)
        tag_ids = payload_dict.pop('tag_ids', None)

        for field, field_val in payload_dict.items():
            setattr(db_item, field, field_val)

        await self._apply_tags_by_ids(db_item, tag_ids)

        await self.repo.commit()
        await self.repo.refresh(db_item, attribute_names=['tags'])

        return self._to_item_out(db_item)

    async def delete(self, obj_id: int) -> int:
        db_item = await self.repo.get_item_for_user(
            item_id=obj_id,
            user_id=self.user_id,
        )
        if db_item is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=self.not_found_msg,
            )

        await self.repo.delete(db_item)
        await self.repo.commit()
        return obj_id

    async def remove_tags(
        self,
        obj_id: int,
        tag_ids: list[int],
    ) -> ItemOut:
        db_item = await self.repo.get_item_for_user(
            item_id=obj_id,
            user_id=self.user_id,
            with_tags=True,
        )
        if db_item is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=self.not_found_msg,
            )

        if not tag_ids:
            return self._to_item_out(db_item)

        ids_to_remove = set(tag_ids)
        db_item.tags = [
            tag for tag in db_item.tags
            if tag.id not in ids_to_remove
        ]

        await self.repo.commit()
        await self.repo.refresh(db_item, attribute_names=['tags'])

        return self._to_item_out(db_item)

    async def _apply_tags_by_ids(
        self,
        db_item: ItemORM,
        tag_ids: list[int] | None,
    ) -> None:
        if tag_ids is None:
            return

        if not tag_ids:
            db_item.tags = []
            return

        tags = await self.repo.get_tags_for_user_by_ids(self.user_id, tag_ids)
        found_ids = {tag.id for tag in tags}
        missing = set(tag_ids) - found_ids
        if missing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f'Tags not found or'
                    f' do not belong to user: {sorted(missing)}'
                ),
            )

        db_item.tags = list(tags)

    @staticmethod
    def _to_item_out(db_item: ItemORM) -> ItemOut:
        return ItemOut(
            id=db_item.id,
            user_id=db_item.user_id,
            title=db_item.title,
            kind=db_item.kind,
            status=db_item.status,
            priority=db_item.priority,
            notes=db_item.notes,
            created_at=db_item.created_at,
            updated_at=db_item.updated_at,
            tag_ids=[tag.id for tag in db_item.tags],
        )
