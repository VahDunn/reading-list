from fastapi import APIRouter, status
from fastapi.params import Depends

from reading_list.api.deps import crud_service_dep
from reading_list.api.schemas.user import UserCreate, UserOut, UserUpdate
from reading_list.repositories.user import UserRepository
from reading_list.services.user import UserService

router = APIRouter(tags=['users'])

UserServiceDep = Depends(crud_service_dep(UserService, UserRepository))


@router.post('', response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_user(
    payload: UserCreate,
    service: UserService = UserServiceDep,
) -> UserOut:
    return await service.create(payload)


@router.get('/{user_id}', response_model=UserOut)
async def get_user(
    user_id: int,
    service: UserService = UserServiceDep,
) -> UserOut:
    return await service.get_by_id(user_id)


@router.get('', response_model=list[UserOut])
async def get_users(
    service: UserService = UserServiceDep,
) -> list[UserOut]:
    return await service.get()


@router.patch('/{user_id}', response_model=UserOut)
async def update_user(
    user_id: int,
    payload: UserUpdate,
    service: UserService = UserServiceDep,
) -> UserOut:
    return await service.update(user_id, payload)


@router.delete('/{user_id}', status_code=status.HTTP_200_OK)
async def delete_user(
    user_id: int,
    service: UserService = UserServiceDep,
) -> int:
    return await service.delete(user_id)
