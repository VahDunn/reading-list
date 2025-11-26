from fastapi import APIRouter

from reading_list.api.v1.items import router as items_router
from reading_list.api.v1.tags import router as tags_router
from reading_list.api.v1.users import router as users_router

api_router = APIRouter()
api_router.include_router(items_router, prefix='/items', tags=['items'])
api_router.include_router(tags_router, prefix='/tags', tags=['tags'])
api_router.include_router(users_router, prefix='/users', tags=['users'])


@api_router.get('/health')
async def health_check():
    return {'status': 'ok'}
