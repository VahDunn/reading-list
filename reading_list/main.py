from contextlib import asynccontextmanager

from fastapi import FastAPI

from reading_list.api.router import api_router
from reading_list.db.engine import engine


@asynccontextmanager
async def lifespan(app_main: FastAPI):
    """
    Жизненный цикл приложения:
    сюда потом положим подключение к БД, прогон миграций, сиды и т.д.
    """
    # startup
    yield
    # shutdown
    await engine.dispose()


def create_app() -> FastAPI:
    main_app = FastAPI(
        title="Reading List API",
        version="1.0.0",
        lifespan=lifespan,
    )

    @main_app.get("/health")
    async def health_check():
        return {"status": "ok"}

    main_app.include_router(api_router, prefix="/api/v1")

    return main_app


app = create_app()
