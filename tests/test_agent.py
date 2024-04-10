from threading import Thread

import pytest
from unittest.mock import patch, MagicMock

from hive_agent.agent import HiveAgent


@pytest.fixture
def agent():
    with patch('hive_agent.agent.OpenAIAgent'), \
            patch('hive_agent.agent.WalletStore'), \
            patch('hive_agent.agent.setup_routes'), \
            patch('uvicorn.run'), \
            patch('hive_agent.agent.signal.signal'):
        return HiveAgent(
            name='TestAgent',
            functions=[lambda x: x],
            host='0.0.0.0',
            port=8000,
            instruction='Test instruction',
            db_url='sqlite+aiosqlite:///hive_agent.db'
        )


def test_agent_initialization(agent):
    assert agent.name == 'TestAgent'
    assert agent.host == '0.0.0.0'
    assert agent.port == 8000
    assert agent.instruction == 'Test instruction'


def test_server_setup(agent):
    with patch('hive_agent.agent.setup_routes') as mock_setup_routes:
        agent._HiveAgent__setup_server('db_url')
        mock_setup_routes.assert_called_once()


def test_run_server(agent):
    with patch('uvicorn.run') as mock_run:
        agent.run_server()
        mock_run.assert_called_once()


def test_signal_handler():
    with patch('hive_agent.agent.signal.signal') as mock_signal, \
         patch('hive_agent.agent.OpenAIAgent'), \
         patch('hive_agent.agent.WalletStore'), \
         patch('hive_agent.agent.setup_routes'), \
         patch('uvicorn.run'):
        agent_instance = HiveAgent(
            name='TestAgent',
            functions=[lambda x: x],
            host='0.0.0.0',
            port=8000,
            instruction='Test instruction',
            db_url='sqlite+aiosqlite:///hive_agent.db'
        )
        agent_instance.shutdown_event = MagicMock()

        thread = Thread(target=agent_instance.run)
        thread.start()
        thread.join(timeout=2)  # timeout necessary to allow signal setup

        # check if signal.signal was called at least twice (for SIGINT and SIGTERM)
        assert mock_signal.call_count >= 2

        # cleanup
        agent_instance.shutdown_event.set()


def test_cleanup(agent):
    agent.db_session = MagicMock()
    agent._HiveAgent__cleanup()
    agent.db_session.close.assert_called_once()
