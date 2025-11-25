from typing import List

from fastapi import APIRouter, Depends, status

from reading_list.api.deps import crud_service_dep
from reading_list.api.schemas.tag import TagCreate, TagOut
from reading_list.repositories.tag import TagRepository
from reading_list.services.tag import TagService

router = APIRouter(tags=['tags'])

TagServiceDep = Depends(crud_service_dep(TagService, TagRepository))


@router.post('', response_model=TagOut, status_code=status.HTTP_201_CREATED)
async def create_tag(
    payload: TagCreate,
    service: TagService = TagServiceDep,
) -> TagOut:
    return await service.create(payload)


@router.get('', response_model=List[TagOut])
async def get_tags(
    service: TagService = TagServiceDep,
) -> List[TagOut]:
    return await service.get()


@router.get('/{tag_id}', response_model=TagOut)
async def get_tag(
    tag_id: int,
    service: TagService = TagServiceDep,
) -> TagOut:
    return await service.get_by_id(tag_id)


@router.delete('/{tag_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(
    tag_id: int,
    service: TagService = TagServiceDep,
) -> None:
    return await service.delete(tag_id)
