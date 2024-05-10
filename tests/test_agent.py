import signal

import pytest
from unittest.mock import MagicMock, patch

from hive_agent.agent import HiveAgent


@pytest.fixture
def agent():
    with patch('hive_agent.agent.OpenAIAgent'), \
            patch('hive_agent.agent.WalletStore'), \
            patch('hive_agent.agent.setup_routes'), \
            patch('uvicorn.Server.serve', new_callable=MagicMock):
        agent = HiveAgent(
            name='TestAgent',
            functions=[lambda x: x],
            host='0.0.0.0',
            port=8000,
            instruction='Test instruction',
            db_url='sqlite+aiosqlite:///hive_agent.db'
        )
    return agent


@pytest.mark.asyncio
async def test_agent_initialization(agent):
    assert agent.name == 'TestAgent'
    assert agent.host == '0.0.0.0'
    assert agent.port == 8000
    assert agent.instruction == 'Test instruction'


def test_server_setup(agent):
    with patch('hive_agent.agent.setup_routes') as mock_setup_routes:
        agent._HiveAgent__setup_server('db_url')
        mock_setup_routes.assert_called_once()


@pytest.mark.asyncio
async def test_run_server(agent):
    with patch('uvicorn.Server.serve', new_callable=MagicMock) as mock_serve:
        await agent.run_server()
        mock_serve.assert_called_once()


def test_signal_handler(agent):
    agent.shutdown_event = MagicMock()
    agent.shutdown_procedures = MagicMock()
    with patch('asyncio.create_task') as mock_create_task:
        agent._HiveAgent__signal_handler(signal.SIGINT, None)
        mock_create_task.assert_called_once_with(agent.shutdown_procedures())


@pytest.mark.asyncio
async def test_cleanup(agent):
    agent.db_session = MagicMock()
    await agent._HiveAgent__cleanup()
    agent.db_session.close.assert_called_once()
