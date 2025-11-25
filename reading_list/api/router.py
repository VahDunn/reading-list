from fastapi import APIRouter

from reading_list.api.v1.items import router as items_router
from reading_list.api.v1.tags import router as tags_router

api_router = APIRouter()
api_router.include_router(items_router, prefix='/items', tags=['items'])
api_router.include_router(tags_router, prefix='/tags', tags=['tags'])
