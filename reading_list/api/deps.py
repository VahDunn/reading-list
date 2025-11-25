from typing import AsyncGenerator, Awaitable, Callable, Type, TypeVar

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from reading_list.db.engine import AsyncSessionLocal
from reading_list.repositories.base_crud import BaseCrudRepository
from reading_list.services.abstract_crud import AbstractCrudService

TRepo = TypeVar('TRepo', bound=BaseCrudRepository)
TService = TypeVar('TService', bound=AbstractCrudService)
x_user_header = Header(default=None, alias='X-User-Id')


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session

depends_db = Depends(get_db)


async def get_current_user_id(
    x_user_id: int | None = x_user_header,
) -> int:
    if x_user_id is None:
        return 1
    if x_user_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='X-User-Id must be positive integer',
        )
    return x_user_id

depends_user_id = Depends(get_current_user_id)


def crud_service_dep(
    service_cls: Type[TService],
    repo_cls: Type[TRepo],
) -> Callable[..., Awaitable[TService]]:
    async def _dep(  # noqa: WPS430
        db: AsyncSession = depends_db,
        user_id: int = depends_user_id,
    ) -> TService:
        repo = repo_cls(db)
        return service_cls(repo=repo, user_id=user_id)
    return _dep
