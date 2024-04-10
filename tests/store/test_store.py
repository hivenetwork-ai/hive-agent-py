import pytest

from unittest.mock import AsyncMock, MagicMock

from hive_agent.store.store import Store


@pytest.fixture
def mock_session_factory():
    session = AsyncMock()
    session_factory = MagicMock(return_value=session)
    session.__aenter__.return_value = session
    session.__aexit__.return_value = AsyncMock()
    return session_factory


@pytest.fixture
def store(mock_session_factory):
    return Store(session_factory=mock_session_factory)


@pytest.mark.asyncio
async def test_add(store, mock_session_factory):
    namespace = "test"
    data = {"key": "value"}

    new_entry = await store.add(namespace, data)

    session = mock_session_factory.return_value.__aenter__.return_value
    session.add.assert_called_once()
    session.commit.assert_awaited_once()

    assert new_entry.namespace == namespace
    assert new_entry.data == data


@pytest.mark.asyncio
async def test_get(store, mock_session_factory):
    namespace = "test"

    await store.get(namespace)

    session = mock_session_factory.return_value.__aenter__.return_value
    session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_by_id(store, mock_session_factory):
    namespace = "test"
    entry_id = 1

    await store.get_by_id(namespace, entry_id)

    session = mock_session_factory.return_value.__aenter__.return_value
    session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_update(store, mock_session_factory):
    namespace = "test"
    entry_id = 1
    new_data = {"name": "Updated Name"}

    await store.update(namespace, entry_id, new_data)

    session = mock_session_factory.return_value.__aenter__.return_value
    session.execute.assert_awaited_once()
    session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete(store, mock_session_factory):
    namespace = "test"
    entry_id = 1

    await store.delete(namespace, entry_id)

    session = mock_session_factory.return_value.__aenter__.return_value
    session.execute.assert_awaited_once()
    session.commit.assert_awaited_once()

