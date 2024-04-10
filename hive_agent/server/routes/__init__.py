from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from llama_index.agent.openai import OpenAIAgent

from .chat import setup_chat_routes
from .entry import setup_entry_routes
from hive_agent.store import Base, Store


def setup_routes(app: FastAPI, agent: OpenAIAgent, db_url: str):
    async_engine = create_async_engine(db_url)
    async_session_factory = sessionmaker(bind=async_engine, class_=AsyncSession)
    store = Store(session_factory=async_session_factory)

    @app.on_event("startup")
    async def startup_event():
        async with async_engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)

    @app.get("/")
    def read_root():
        return "Hive Agent is running"

    setup_chat_routes(app, agent)
    setup_entry_routes(app, store)
