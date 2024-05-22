import pytest

from fastapi import APIRouter, FastAPI
from httpx import ASGITransport, AsyncClient
from unittest.mock import MagicMock, AsyncMock

from hive_agent.server.routes.entry import setup_entry_routes
from hive_agent.store import Store


@pytest.fixture
def session_factory():
    return AsyncMock()


@pytest.fixture
def store(session_factory):
    return Store(session_factory=session_factory)


@pytest.fixture
def app(store):
    app = FastAPI()
    v1_router = APIRouter()
    setup_entry_routes(v1_router, store)
    app.include_router(v1_router, prefix="/api/v1")
    return app


@pytest.fixture
async def client(app):
    async with AsyncClient(base_url="test://db", transport=ASGITransport(app)) as test_client:
        yield test_client


@pytest.mark.asyncio
async def test_create_entry(client, store, mocker):
    namespace = "test"
    data = {"key": "value"}

    mock_entry = MagicMock(id=1)
    mocker.patch.object(store, 'add', return_value=mock_entry)

    response = await client.post(f"/api/v1/entry/{namespace}", json=data)
    assert response.status_code == 200
    assert response.json() == {
        "status": "entry created",
        "data": {
            "namespace": namespace,
            "entry_id": mock_entry.id
        }
    }

@pytest.mark.asyncio
async def test_get_entries_with_empty_json(client, store):
    namespace = "test"
    mocked_entry = MagicMock(to_dict=lambda: {})

    store.get = AsyncMock(return_value=[mocked_entry])
    response = await client.get(f"/api/v1/entry/{namespace}")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_get_entries_with_invalid_namespace(client, store):
    namespace = "not_valid_*^(*&$#)"
    mocked_entry = MagicMock(to_dict=lambda: {'id': 1, 'data': 'test'})

    store.get = AsyncMock(return_value=[mocked_entry])

    response = await client.get(f"/api/v1/entry/{namespace}")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_get_entries(client, store):
    namespace = "test"
    mocked_entry = MagicMock(to_dict=lambda: {'id': 1, 'data': 'test'})

    store.get = AsyncMock(return_value=[mocked_entry])

    response = await client.get(f"/api/v1/entry/{namespace}")
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["status"] == "entries retrieved successfully"
    assert len(response_data["data"]["entries"]) == 1
    print(response_data)
    assert response_data["data"]["entries"][0]['id'] == 1


@pytest.mark.asyncio
async def test_get_entry_by_id(client, store):
    namespace = "test"
    entry_id = 5
    mocked_entry = MagicMock(to_dict=lambda: {'id': entry_id, 'data': 'test'})

    store.get_by_id = AsyncMock(return_value=mocked_entry.to_dict())

    response = await client.get(f"/api/v1/entry/{namespace}/{entry_id}")
    assert response.status_code == 200

    response_data = response.json()

    assert response_data["status"] == "entry retrieved successfully"
    print(response_data)
    assert response_data["data"]["entry"]["data"] == 'test'


@pytest.mark.asyncio
async def test_update_entry(client, store):
    namespace = "test"
    entry_id = "1"
    new_data = {'data': 'updated'}

    store.update = AsyncMock(return_value=None)

    response = await client.put(f"/api/v1/entry/{namespace}/{entry_id}", json=new_data)
    assert response.status_code == 200
    assert response.json()["status"] == "entry updated"
    store.update.assert_awaited_once_with(namespace, entry_id, new_data)


@pytest.mark.asyncio
async def test_delete_entry(client, store):
    namespace = "test"
    entry_id = "1"

    store.delete = AsyncMock(return_value=None)

    response = await client.delete(f"/api/v1/entry/{namespace}/{entry_id}")
    assert response.status_code == 200
    assert response.json()["status"] == "entry removed"
    store.delete.assert_awaited_once_with(namespace, entry_id)
