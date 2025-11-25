from datetime import datetime
from typing import List, Literal

from pydantic import BaseModel

from reading_list.db.models.item import ItemKind, ItemPriority, ItemStatus


class ItemFilters(BaseModel):
    status: ItemStatus | None = None
    kind: ItemKind | None = None
    priority: ItemPriority | None = None
    tag_ids: List[int] | None = None
    q: str | None = None  # noqa: WPS111
    created_from: datetime | None = None
    created_to: datetime | None = None
    limit: int = 20
    offset: int = 0
    sort_by: Literal['created_at', 'updated_at', 'priority'] = 'created_at'
    sort_dir: Literal['asc', 'desc'] = 'desc'
