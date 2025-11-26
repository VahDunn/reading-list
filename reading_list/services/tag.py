from fastapi import HTTPException, status

from reading_list.api.schemas.tag import TagCreate, TagOut
from reading_list.db.models.tag import TagORM
from reading_list.repositories.tag import TagRepository
from reading_list.services.abstract_crud import AbstractCrudService


class TagService(AbstractCrudService[TagCreate, TagCreate, TagOut, None]):
    def __init__(self, repo: TagRepository, user_id: int):
        self.repo = repo
        self.user_id = user_id

    async def get_by_id(self, obj_id: int) -> TagOut:
        tag = await self.repo.get_by_id(obj_id)
        if tag is None or tag.user_id != self.user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Tag not found',
            )
        return self._to_tag_out(tag)

    async def get(self, filters: None = None) -> list[TagOut]:
        tags = await self.repo.get_for_user(self.user_id)
        return [self._to_tag_out(tag) for tag in tags]

    async def create(self, payload: TagCreate) -> TagOut:
        existing = await self.repo.get_by_name_for_user(
            self.user_id, payload.name
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Tag with this name already exists',
            )

        tag = TagORM(
            user_id=self.user_id,
            name=payload.name,
        )
        await self.repo.add(tag)
        await self.repo.commit()
        await self.repo.refresh(tag)
        return self._to_tag_out(tag)

    async def update(self, obj_id: int, payload: TagCreate) -> TagOut:
        tag: TagORM = await self.repo.get_by_id(obj_id)
        if tag is None or tag.user_id != self.user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Tag not found',
            )

        tag.name = payload.name
        await self.repo.commit()
        await self.repo.refresh(tag)
        return self._to_tag_out(tag)

    async def delete(self, obj_id: int) -> int:
        tag = await self.repo.get_by_id(obj_id)
        if tag is None or tag.user_id != self.user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Tag not found',
            )
        await self.repo.delete(tag)
        await self.repo.commit()
        return obj_id

    @staticmethod
    def _to_tag_out(tag: TagORM) -> TagOut:
        return TagOut(
            id=tag.id,
            user_id=tag.user_id,
            name=tag.name,
        )
