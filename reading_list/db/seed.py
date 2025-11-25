import asyncio

from sqlalchemy import select

from reading_list.db.engine import AsyncSessionLocal
from reading_list.db.models.item import (ItemKind, ItemORM, ItemPriority,
                                         ItemStatus)
from reading_list.db.models.tag import TagORM
from reading_list.db.models.user import UserORM


async def run_seed() -> None:
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(UserORM))
        existing_users = result.scalars().all()
        if existing_users:
            print('Seed: users already exist, skipping.')
            return

        # --- Users ---
        melinoe = UserORM(email='melinoe@example.com', display_name='Melinoe')
        zagreus = UserORM(email='zagreus@example.com', display_name='Zagreus')

        session.add_all([melinoe, zagreus])
        await session.flush()

        tag_work = TagORM(user_id=melinoe.id, name='work')
        tag_learning = TagORM(user_id=melinoe.id, name='learning')
        tag_important = TagORM(user_id=melinoe.id, name='important')
        tag_hobby = TagORM(user_id=melinoe.id, name='hobby')

        tag_reading = TagORM(user_id=zagreus.id, name='reading')
        tag_later = TagORM(user_id=zagreus.id, name='later')

        session.add_all(
            [
                tag_work,
                tag_learning,
                tag_important,
                tag_hobby,
                tag_reading,
                tag_later,
            ]
        )
        await session.flush()

        items_melinoe = [
            ItemORM(
                user_id=melinoe.id,
                title='Shallow Blue Earth',
                kind=ItemKind.book,
                status=ItemStatus.reading,
                priority=ItemPriority.high,
                notes='Читаю по вечерам, осталось ~30%.',
                tags=[tag_important, tag_learning],
            ),
            ItemORM(
                user_id=melinoe.id,
                title='Deep Green Sky',
                kind=ItemKind.book,
                status=ItemStatus.planned,
                priority=ItemPriority.normal,
                notes='В очередь после Shallow Blue Earth.',
                tags=[tag_work],
            ),
            ItemORM(
                user_id=melinoe.id,
                title='FastAPI Official Tutorial',
                kind=ItemKind.article,
                status=ItemStatus.reading,
                priority=ItemPriority.high,
                notes='Разобраться с зависимостями и background tasks.',
                tags=[tag_learning],
            ),
            ItemORM(
                user_id=melinoe.id,
                title='Мифы Древней Греции и Древнего Рима',
                kind=ItemKind.article,
                status=ItemStatus.done,
                priority=ItemPriority.low,
                notes='Просто для интереса, уже прочитано.',
                tags=[tag_hobby],
            ),
            ItemORM(
                user_id=melinoe.id,
                title='М. Елизаров - Земля',
                kind=ItemKind.book,
                status=ItemStatus.planned,
                priority=ItemPriority.normal,
                notes='Хочу прочитать в этом году.',
                tags=[tag_important, tag_work],
            ),
        ]

        items_zagreus = [
            ItemORM(
                user_id=zagreus.id,
                title='Е. Водолазкин - Лавр',
                kind=ItemKind.article,
                status=ItemStatus.planned,
                priority=ItemPriority.low,
                notes='Читаю в свободное время',
                tags=[tag_reading],
            ),
            ItemORM(
                user_id=zagreus.id,
                title='Почему Тарковский - гений?',
                kind=ItemKind.book,
                status=ItemStatus.planned,
                priority=ItemPriority.low,
                notes='Когда-нибудь потом.',
                tags=[tag_later],
            ),
        ]

        session.add_all(items_melinoe + items_zagreus)
        await session.commit()


if __name__ == '__main__':
    asyncio.run(run_seed())
