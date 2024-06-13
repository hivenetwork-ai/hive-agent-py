import os
from dotenv import load_dotenv
from typing import Any

from fastapi import FastAPI, APIRouter


from .chat import setup_chat_routes
from .database import setup_database_routes
from .files import setup_files_routes

from hive_agent.database.database import initialize_db, get_db, setup_chats_table


load_dotenv()


def setup_routes(app: FastAPI, agent: Any):

    @app.on_event("startup")
    async def startup_event():
        db_url = os.getenv("HIVE_AGENT_DATABASE_URL")
        if db_url:
            print(f"db url in startup_event: {db_url}")
        else:
            print("HIVE_AGENT_DATABASE_URL is not set")

        await initialize_db()

        print(f'db url after init is: {os.getenv("HIVE_AGENT_DATABASE_URL")}')

        async for db in get_db():
            await setup_chats_table(db)

    @app.get("/")
    def read_root():
        return "Hive Agent is running"

    v1 = APIRouter()

    setup_database_routes(v1)
    setup_chat_routes(v1, agent)
    setup_files_routes(v1)

    app.include_router(v1, prefix="/api/v1")
