from datetime import datetime
from enum import StrEnum, auto
from typing import List

import sqlalchemy as sa
from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import functions as sa_func

from reading_list.db.models.base import BaseORM
from reading_list.db.models.tag import TagORM
from reading_list.db.models.user import UserORM


class ItemKind(StrEnum):
    book = auto()
    article = auto()


class ItemStatus(StrEnum):
    planned = auto()
    reading = auto()
    done = auto()


class ItemPriority(StrEnum):
    low = auto()
    normal = auto()
    high = auto()


class ItemORM(BaseORM):
    __tablename__ = 'items'

    user_id: Mapped[int] = mapped_column(
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
    )

    title: Mapped[str] = mapped_column(
        String(),
        nullable=False,
    )

    kind: Mapped[ItemKind] = mapped_column(
        sa.Enum(ItemKind, name='item_kind'),
        nullable=False,
    )

    status: Mapped[ItemStatus] = mapped_column(
        sa.Enum(ItemStatus, name='item_status'),
        nullable=False,
    )

    priority: Mapped[ItemPriority] = mapped_column(
        sa.Enum(ItemPriority, name='item_priority'),
        nullable=False,
        default=ItemPriority.normal,
        server_default=ItemPriority.normal.value,
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    updated_at: Mapped[datetime] = mapped_column(
        sa.TIMESTAMP(timezone=True),
        sa.FetchedValue(),
        server_default=sa_func.now(),
        onupdate=sa_func.now(),
        nullable=False,
    )
    user: Mapped[UserORM] = relationship(
        back_populates='items',
    )
    tags: Mapped[List[TagORM]] = relationship(
        secondary='item_tags',
        back_populates='items',
    )
