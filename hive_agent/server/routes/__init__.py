from dotenv import load_dotenv
from typing import Any

from fastapi import FastAPI, APIRouter


from .chat import setup_chat_routes
from .database import setup_database_routes
from .files import setup_files_routes
from .vectorindex import setup_vectorindex_routes

from hive_agent.database.database import initialize_db, get_db, setup_chats_table
from hive_agent.sdk_context import SDKContext


load_dotenv()


def setup_routes(app: FastAPI, id: str,sdk_context: SDKContext):

    @app.on_event("startup")
    async def startup_event():

        await initialize_db()

        async for db in get_db():
            await setup_chats_table(db)

    @app.get("/")
    def read_root():
        return {"message": "Hive Agent is running"}

    v1 = APIRouter()

    setup_database_routes(v1)
    setup_chat_routes(v1, id, sdk_context)
    setup_files_routes(v1, id, sdk_context)
    setup_vectorindex_routes(v1)

    app.include_router(v1, prefix="/api/v1")
