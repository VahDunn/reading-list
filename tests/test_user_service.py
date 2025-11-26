from datetime import datetime, timezone

import pytest
from fastapi import HTTPException, status

from reading_list.db.models import item as item_model
from reading_list.db.models import tag as tag_model
from reading_list.db.models.user import UserORM

from reading_list.api.schemas.user import UserCreate, UserUpdate
from reading_list.services.user import UserService



class FakeUserRepository:
    """Простейший in-memory репозиторий для UserService."""

    def __init__(self) -> None:
        self._store: dict[int, UserORM] = {}
        self._id_seq: int = 1

    async def get_by_id(self, obj_id: int) -> UserORM | None:
        return self._store.get(obj_id)

    async def get_all(self) -> list[UserORM]:
        return list(self._store.values())

    async def get_by_email(self, email: str) -> UserORM | None:
        for user in self._store.values():
            if user.email == email:
                return user
        return None

    async def add(self, orm_model: UserORM) -> UserORM:
        orm_model.id = self._id_seq
        self._id_seq += 1

        if getattr(orm_model, "created_at", None) is None:
            orm_model.created_at = datetime.now(timezone.utc)

        self._store[orm_model.id] = orm_model
        return orm_model

    async def delete(self, db_obj: UserORM) -> None:
        self._store.pop(db_obj.id, None)

    async def commit(self) -> None:
        return None

    async def refresh(self, db_obj: UserORM) -> UserORM:
        return db_obj


@pytest.fixture
def user_repo() -> FakeUserRepository:
    return FakeUserRepository()


@pytest.fixture
def user_service(user_repo: FakeUserRepository) -> UserService:
    return UserService(repo=user_repo, user_id=1)


@pytest.mark.asyncio
async def test_create_user_success(user_service: UserService):
    payload = UserCreate(
        email="alice@example.com",
        display_name="Alice",
    )

    user = await user_service.create(payload)

    assert user.id is not None
    assert user.email == payload.email
    assert user.display_name == payload.display_name
    assert user.created_at is not None


@pytest.mark.asyncio
async def test_create_user_duplicate_email_raises(user_service: UserService):
    payload = UserCreate(
        email="alice@example.com",
        display_name="Alice",
    )
    await user_service.create(payload)

    # вторая попытка с тем же email
    with pytest.raises(HTTPException) as exc_info:
        await user_service.create(
            UserCreate(
                email="alice@example.com",
                display_name="Alice Dup",
            )
        )

    exc = exc_info.value
    assert exc.status_code == status.HTTP_400_BAD_REQUEST
    assert "already exists" in exc.detail


@pytest.mark.asyncio
async def test_get_user_by_id_success(user_service: UserService):
    created = await user_service.create(
        UserCreate(
            email="bob@example.com",
            display_name="Bob",
        )
    )

    user = await user_service.get_by_id(created.id)

    assert user.id == created.id
    assert user.email == "bob@example.com"
    assert user.display_name == "Bob"


@pytest.mark.asyncio
async def test_get_user_by_id_not_found(user_service: UserService):
    with pytest.raises(HTTPException) as exc_info:
        await user_service.get_by_id(999)

    exc = exc_info.value
    assert exc.status_code == status.HTTP_404_NOT_FOUND
    assert exc.detail == "User not found"


@pytest.mark.asyncio
async def test_get_all_users(user_service: UserService):
    await user_service.create(
        UserCreate(email="u1@example.com", display_name="User1")
    )
    await user_service.create(
        UserCreate(email="u2@example.com", display_name="User2")
    )

    users = await user_service.get()

    assert len(users) == 2
    emails = {u.email for u in users}
    assert emails == {"u1@example.com", "u2@example.com"}


@pytest.mark.asyncio
async def test_update_user_success(user_service: UserService):
    created = await user_service.create(
        UserCreate(
            email="charlie@example.com",
            display_name="Charlie",
        )
    )

    updated = await user_service.update(
        created.id,
        UserUpdate(
            display_name="Charlie Updated",
        ),
    )

    assert updated.id == created.id
    assert updated.email == "charlie@example.com"
    assert updated.display_name == "Charlie Updated"


@pytest.mark.asyncio
async def test_update_user_email_conflict(user_service: UserService):
    u1 = await user_service.create(
        UserCreate(
            email="user1@example.com",
            display_name="User1",
        )
    )
    u2 = await user_service.create(
        UserCreate(
            email="user2@example.com",
            display_name="User2",
        )
    )

    with pytest.raises(HTTPException) as exc_info:
        await user_service.update(
            u2.id,
            UserUpdate(email=u1.email),
        )

    exc = exc_info.value
    assert exc.status_code == status.HTTP_400_BAD_REQUEST
    assert "already exists" in exc.detail


@pytest.mark.asyncio
async def test_delete_user_success(user_service: UserService):
    created = await user_service.create(
        UserCreate(
            email="delete_me@example.com",
            display_name="ToDelete",
        )
    )

    deleted_id = await user_service.delete(created.id)
    assert deleted_id == created.id

    with pytest.raises(HTTPException) as exc_info:
        await user_service.get_by_id(created.id)

    exc = exc_info.value
    assert exc.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_delete_user_not_found(user_service: UserService):
    with pytest.raises(HTTPException) as exc_info:
        await user_service.delete(999)

    exc = exc_info.value
    assert exc.status_code == status.HTTP_404_NOT_FOUND
    assert exc.detail == "User not found"
