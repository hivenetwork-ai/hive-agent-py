from unittest.mock import MagicMock, patch

import pytest
from hive_agent.chat import ChatManager
from llama_index.agent.openai import OpenAIAgent  # type: ignore
from llama_index.core.llms import ChatMessage, MessageRole
from llama_index.multi_modal_llms.openai import \
    OpenAIMultiModal  # type: ignore


class MockAgent:
    async def astream_chat(self, content, chat_history=None):
        async def async_response_gen():
            yield "chat response"

        return type("MockResponse", (), {"async_response_gen": async_response_gen})

    async def achat(self, content, chat_history=None):
        return type("MockResponse", (), {"response": "chat response"})


class MockMultiModalAgent:
    def create_task(self, content, extra_state=None):
        return type("MockTask", (), {"task_id": "12345"})

    async def _arun_step(self, task_id):
        return type("MockResponse", (), {"is_last": True})

    def finalize_response(self, task_id):
        return "multimodal response"


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
def multi_modal_agent():
    # Mocking the methods within the agent to make them MagicMock objects
    agent = MockMultiModalAgent()
    agent._arun_step = MagicMock(side_effect=agent._arun_step)
    agent.finalize_response = MagicMock(side_effect=agent.finalize_response)
    return agent


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
async def test_generate_response_with_generic_llm(agent, db_manager):
    chat_manager = ChatManager(agent, user_id="123", session_id="abc")
    user_message = ChatMessage(role=MessageRole.USER, content="Hello!")

    response = await chat_manager.generate_response(db_manager, user_message, [])
    assert response == "chat response"

    messages = await chat_manager.get_messages(db_manager)
    assert len(messages) == 2
    assert messages[0].content == "Hello!"
    assert messages[1].content == "chat response"


@pytest.mark.asyncio
async def test_get_all_chats_for_user(agent, db_manager):
    chat_manager1 = ChatManager(agent, user_id="123", session_id="abc")
    await chat_manager1.add_message(db_manager, MessageRole.USER, "Hello in abc")
    await chat_manager1.add_message(db_manager, MessageRole.ASSISTANT, "Response in abc")

    chat_manager2 = ChatManager(agent, user_id="123", session_id="def")
    await chat_manager2.add_message(db_manager, MessageRole.USER, "Hello in def")
    await chat_manager2.add_message(db_manager, MessageRole.ASSISTANT, "Response in def")

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


@pytest.mark.asyncio
async def test_generate_response_with_openai_multimodal(multi_modal_agent, db_manager):
    with patch("llama_index.core.settings._Settings.llm", new=MagicMock(spec=OpenAIMultiModal)):
        chat_manager = ChatManager(multi_modal_agent, user_id="123", session_id="abc", enable_multi_modal=True)
        user_message = ChatMessage(role=MessageRole.USER, content="Hello!")
        image_document_paths = ["image1.png", "image2.png"]

        response = await chat_manager.generate_response(db_manager, user_message, image_document_paths)

        assert response == "multimodal response"

        messages = await chat_manager.get_messages(db_manager)
        assert len(messages) == 2
        assert messages[0].content == "Hello!"
        assert messages[1].content == "multimodal response"


@pytest.mark.asyncio
async def test_execute_task_success(multi_modal_agent):
    chat_manager = ChatManager(multi_modal_agent, user_id="123", session_id="abc")

    result = await chat_manager._execute_task("task_id_123")

    assert result == "multimodal response"
    multi_modal_agent._arun_step.assert_called_once_with("task_id_123")
    multi_modal_agent.finalize_response.assert_called_once_with("task_id_123")


@pytest.mark.asyncio
async def test_execute_task_with_exception(multi_modal_agent):
    async def mock_arun_step(task_id):
        raise ValueError(f"Could not find step_id: {task_id}")

    multi_modal_agent._arun_step = MagicMock(side_effect=mock_arun_step)

    chat_manager = ChatManager(multi_modal_agent, user_id="123", session_id="abc")

    result = await chat_manager._execute_task("task_id_123")

    assert result == "error during step execution: Could not find step_id: task_id_123"
    multi_modal_agent._arun_step.assert_called_once_with("task_id_123")


@pytest.mark.asyncio
async def test_generate_response_with_openai_agent(agent, db_manager):
    with patch("llama_index.core.settings._Settings.llm", new=MagicMock(spec=OpenAIAgent)):
        chat_manager = ChatManager(agent, user_id="123", session_id="abc")
        user_message = ChatMessage(role=MessageRole.USER, content="Hello!")

        response = await chat_manager.generate_response(db_manager, user_message, [])
        assert response == "chat response"

        messages = await chat_manager.get_messages(db_manager)
        assert len(messages) == 2
        assert messages[0].content == "Hello!"
        assert messages[1].content == "chat response"
