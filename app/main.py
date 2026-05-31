from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import init_db
from app.routes import router
from app.settings import load_environment


load_environment()


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    init_db()
    yield


def create_app() -> FastAPI:
    api = FastAPI(title="Stock Analysis API", version="0.1.0", lifespan=lifespan)
    api.include_router(router)
    return api


app = create_app()
