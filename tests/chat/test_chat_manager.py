import pytest

from llama_index.core.llms import ChatMessage, MessageRole
from hive_agent.chat import ChatManager


class MockAgent:
    async def astream_chat(self, content, chat_history=None):
        async def async_response_gen():
            yield "chat response"

        return type("MockResponse", (), {"async_response_gen": async_response_gen})

    async def achat(self, content, chat_history=None):
        return type("MockResponse", (), {"message": "chat response"})


class MockDatabaseManager:
    def __init__(self):
        self.data = []

    async def insert_data(self, table_name: str, data: dict):
        self.data.append(data)

    async def read_data(self, table_name: str, filters: dict):
        return [d for d in self.data if all(d[k] == v[0] for k, v in filters.items())]


@pytest.fixture
def agent():
    return MockAgent()


@pytest.fixture
def db_manager():
    return MockDatabaseManager()


@pytest.mark.asyncio
async def test_add_message(agent, db_manager):
    chat_manager = ChatManager(agent, user_id="123", session_id="abc")
    await chat_manager.add_message(db_manager, MessageRole.USER, "Hello!")
    messages = await chat_manager.get_messages(db_manager)
    assert len(messages) == 1
    assert messages[0].content == "Hello!"


@pytest.mark.asyncio
async def test_generate_response(agent, db_manager):
    chat_manager = ChatManager(agent, user_id="123", session_id="abc")
    user_message = ChatMessage(role=MessageRole.USER, content="Hello!")
    response = await chat_manager.generate_response(db_manager, [user_message], user_message)
    assert response == "chat response"
    messages = await chat_manager.get_messages(db_manager)
    assert len(messages) == 2
    assert messages[0].content == "Hello!"
    assert messages[1].content == "chat response"
