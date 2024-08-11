import json
import pytest
from unittest.mock import AsyncMock

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.future import select

from hive_agent.database.database import DatabaseManager

Base = declarative_base()

@pytest.fixture
def mock_session(mocker):
    session_mock = mocker.AsyncMock(spec=AsyncSession)
    # Setup the execute method to return a mock that simulates 'result.scalars().first()'
    result_mock = mocker.MagicMock()
    scalar_mock = mocker.MagicMock()
    scalar_mock.first.return_value = None 
    result_mock.scalars.return_value = scalar_mock
    session_mock.execute = mocker.AsyncMock(return_value=result_mock)
    return session_mock

@pytest.fixture
def db_manager(mock_session, mocker):
    mocker.patch("hive_agent.database.database.DatabaseManager.__init__", return_value=None)
    manager = DatabaseManager(mock_session)
    manager.db = mock_session
    return manager

@pytest.mark.asyncio
async def test_create_table(db_manager, mock_session):
    columns = {"name": "String", "age": "Integer"}
    await db_manager.create_table("users", columns)
    mock_session.execute.assert_called_once()

@pytest.mark.asyncio
async def test_insert_data(db_manager, mock_session):
    table_definition = json.dumps({"name": "String", "age": "Integer"})
    db_manager.get_table_definition = AsyncMock(return_value=table_definition)
    data = {"name": "John", "age": 30}
    await db_manager.insert_data("users", data)
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()

@pytest.mark.asyncio
async def test_update_data(db_manager, mock_session):
    table_definition = json.dumps({"name": "String", "age": "Integer"})
    db_manager.get_table_definition = AsyncMock(return_value=table_definition)
    mock_instance = AsyncMock(name="John", age=30)
    db_manager.db.get.return_value = mock_instance
    new_data = {"name": "Jane", "age": 35}
    await db_manager.update_data("users", 1, new_data)
    assert mock_instance.name == "Jane"
    assert mock_instance.age == 35
    mock_session.commit.assert_called_once()

@pytest.mark.asyncio
async def test_delete_data(db_manager, mock_session):
    table_definition = json.dumps({"name": "String", "age": "Integer"})
    db_manager.get_table_definition = AsyncMock(return_value=table_definition)
    mock_instance = AsyncMock()
    db_manager.db.get.return_value = mock_instance
    await db_manager.delete_data("users", 1)
    mock_session.delete.assert_called_once_with(mock_instance)
    mock_session.commit.assert_called_once()

