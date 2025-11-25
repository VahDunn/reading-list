from typing import Generic, List, TypeVar

from pydantic import BaseModel

MAX_TITLE_LENGTH = 255

T = TypeVar('T')  # noqa: WPS111


class PageMeta(BaseModel):
    total: int
    limit: int
    offset: int


class Page(BaseModel, Generic[T]):
    items_list: List[T]
    meta: PageMeta
