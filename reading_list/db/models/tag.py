from typing import TYPE_CHECKING, List

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from reading_list.db.models.base import Base, BaseORM

if TYPE_CHECKING:
    from reading_list.db.models import ItemORM, UserORM


class TagORM(BaseORM):

    __tablename__ = 'tags'
    __table_args__ = (
        UniqueConstraint(
            'user_id',
            'name',
            name='uq_tags_user_id_name',
        ),
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(
        String(),
        nullable=False,
    )

    user: Mapped['UserORM'] = relationship(
        back_populates='tags',
    )
    items: Mapped[List['ItemORM']] = relationship(  # noqa:WPS110
        secondary='item_tags',
        back_populates='tags',
    )


class ItemTagORM(Base):

    __tablename__ = 'item_tags'

    item_id: Mapped[int] = mapped_column(
        ForeignKey('items.id', ondelete='CASCADE'),
        primary_key=True,
    )
    tag_id: Mapped[int] = mapped_column(
        ForeignKey('tags.id', ondelete='CASCADE'),
        primary_key=True,
    )
