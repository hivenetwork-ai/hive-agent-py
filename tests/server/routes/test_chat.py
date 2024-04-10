import pytest
from fastapi import FastAPI, status
from httpx import AsyncClient

from llama_index.core.llms import MessageRole
from hive_agent.server.routes.chat import setup_chat_routes


class MockAgent:
    async def astream_chat(self, content, messages):
        async def async_response_gen():
            yield "chat response"

        return type('MockResponse', (), {"async_response_gen": async_response_gen})


@pytest.fixture
def agent():
    return MockAgent()


@pytest.fixture
def app(agent):
    fastapi_app = FastAPI()
    setup_chat_routes(fastapi_app, agent)
    return fastapi_app


@pytest.fixture
async def client(app):
    async with AsyncClient(app=app, base_url="http://test") as test_client:
        yield test_client


@pytest.mark.asyncio
async def test_chat_no_messages(client):
    data = {"messages": []}
    response = await client.post("/api/chat", json=data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "No messages provided" in response.json()["detail"]


@pytest.mark.asyncio
async def test_chat_last_message_not_user(client):
    data = {
        "messages": [
            {"role": MessageRole.SYSTEM, "content": "System message"},
            {"role": MessageRole.USER, "content": "User message"},
            {"role": MessageRole.SYSTEM, "content": "Another system message"}
        ]
    }
    response = await client.post("/api/chat", json=data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Last message must be from user" in response.json()["detail"]


@pytest.mark.asyncio
async def test_chat_success(client, agent):
    data = {
        "messages": [
            {"role": MessageRole.USER, "content": "Hello!"}
        ]
    }
    response = await client.post("/api/chat", json=data)
    assert response.status_code == status.HTTP_200_OK
    assert response.text == "chat response"
