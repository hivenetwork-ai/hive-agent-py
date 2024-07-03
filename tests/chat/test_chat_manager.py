import pytest

from llama_index.core.llms import ChatMessage, MessageRole
from hive_agent.chat import ChatManager


class MockAgent:
    async def astream_chat(self, content, chat_history=None):
        async def async_response_gen():
            yield "chat response"

        return type("MockResponse", (), {"async_response_gen": async_response_gen})

    async def achat(self, content, chat_history=None):
        return type("MockResponse", (), {"response": "chat response"})


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

    response = await chat_manager.generate_response(
        db_manager, [user_message], user_message
    )
    assert response == "chat response"

    messages = await chat_manager.get_messages(db_manager)
    assert len(messages) == 2
    assert messages[0].content == "Hello!"
    assert messages[1].content == "chat response"


@pytest.mark.asyncio
async def test_get_all_chats_for_user(agent, db_manager):
    chat_manager1 = ChatManager(agent, user_id="123", session_id="abc")
    await chat_manager1.add_message(db_manager, MessageRole.USER, "Hello in abc")
    await chat_manager1.add_message(
        db_manager, MessageRole.ASSISTANT, "Response in abc"
    )

    chat_manager2 = ChatManager(agent, user_id="123", session_id="def")
    await chat_manager2.add_message(db_manager, MessageRole.USER, "Hello in def")
    await chat_manager2.add_message(
        db_manager, MessageRole.ASSISTANT, "Response in def"
    )

    chat_manager = ChatManager(agent, user_id="123", session_id="")
    all_chats = await chat_manager.get_all_chats_for_user(db_manager)

    assert "abc" in all_chats
    assert "def" in all_chats

    assert len(all_chats["abc"]) == 2
    assert all_chats["abc"][0]["message"] == "Hello in abc"
    assert all_chats["abc"][1]["message"] == "Response in abc"

    assert len(all_chats["def"]) == 2
    assert all_chats["def"][0]["message"] == "Hello in def"
    assert all_chats["def"][1]["message"] == "Response in def"
