from fastapi import APIRouter, status
from fastapi.params import Depends

from reading_list.api.deps import crud_service_dep
from reading_list.api.schemas.item import ItemUpdate  # noqa: WPS318, WPS319
from reading_list.api.schemas.item import ItemCreate, ItemOut, ItemPage
from reading_list.api.schemas.item_filters import ItemFilters
from reading_list.repositories.item import ItemRepository
from reading_list.services.item import ItemsService

router = APIRouter(tags=['items'])

ItemServiceDep = Depends(crud_service_dep(ItemsService, ItemRepository))
ItemFiltersDep = Depends(ItemFilters)


@router.post('', response_model=ItemOut, status_code=status.HTTP_201_CREATED)
async def create_item(
    payload: ItemCreate,
    service: ItemsService = ItemServiceDep,
) -> ItemOut:
    return await service.create(payload)


@router.get('/{item_id}', response_model=ItemOut)
async def get_item(
    item_id: int,
    service: ItemsService = ItemServiceDep,
) -> ItemOut:
    return await service.get_by_id(item_id)


@router.get('', response_model=ItemPage)
async def get_items(
    filters: ItemFilters = ItemFiltersDep,
    service: ItemsService = ItemServiceDep,
) -> ItemPage:
    return await service.get(filters)


@router.patch('/{item_id}', response_model=ItemOut)
async def update_item(
    item_id: int,
    payload: ItemUpdate,
    service: ItemsService = ItemServiceDep,
) -> ItemOut:
    return await service.update(item_id, payload)


@router.delete('/{item_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(
    item_id: int,
    service: ItemsService = ItemServiceDep,
) -> None:
    return await service.delete(item_id)
