from typing import TYPE_CHECKING, List

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from reading_list.db.models.base import BaseORM

if TYPE_CHECKING:
    from reading_list.db.models import ItemORM, TagORM


class UserORM(BaseORM):
    __tablename__ = 'users'

    email: Mapped[str] = mapped_column(
        String(),
        unique=True,
        index=True,
        nullable=False,
    )
    display_name: Mapped[str] = mapped_column(
        String(),
        nullable=False,
    )

    items: Mapped[List['ItemORM']] = relationship(  # noqa:WPS110
        back_populates='user',
        cascade='all, delete-orphan',
    )
    tags: Mapped[List['TagORM']] = relationship(
        back_populates='user',
        cascade='all, delete-orphan',
    )
