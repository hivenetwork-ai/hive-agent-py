import signal
import pytest

from unittest.mock import MagicMock, patch

from hive_agent.agent import HiveAgent


@pytest.fixture
def agent():
    with patch("hive_agent.agent.OpenAILLM"), patch(
        "hive_agent.agent.ClaudeLLM"
    ), patch("hive_agent.agent.MistralLLM"), patch("hive_agent.agent.OllamaLLM"), patch(
        "hive_agent.wallet.WalletStore"
    ), patch(
        "hive_agent.agent.setup_routes"
    ), patch(
        "uvicorn.Server.serve", new_callable=MagicMock
    ):
        test_agent = HiveAgent(
            name="TestAgent",
            functions=[lambda x: x],
            config_path="./hive_config_test.toml",
            host="0.0.0.0",
            port=8000,
            instruction="Test instruction",
            role="user"
        )
    return test_agent


@pytest.mark.asyncio
async def test_agent_initialization(agent):
    assert agent.name == "TestAgent"
    assert agent.config_path == "./hive_config_test.toml"
    assert agent.host == "0.0.0.0"
    assert agent.port == 8000
    assert agent.instruction == "Test instruction"
    assert agent.role == "user"


def test_server_setup(agent):
    with patch("hive_agent.agent.setup_routes") as mock_setup_routes:
        agent._HiveAgent__setup_server()
        mock_setup_routes.assert_called_once()


@pytest.mark.asyncio
async def test_run_server(agent):
    with patch("uvicorn.Server.serve", new_callable=MagicMock) as mock_serve:
        await agent.run_server()
        mock_serve.assert_called_once()


def test_signal_handler(agent):
    agent.shutdown_event = MagicMock()
    agent.shutdown_procedures = MagicMock()
    with patch("asyncio.create_task") as mock_create_task:
        agent._HiveAgent__signal_handler(signal.SIGINT, None)
        mock_create_task.assert_called_once_with(agent.shutdown_procedures())


def test_server_setup_exception(agent):
    with patch("hive_agent.agent.setup_routes") as mock_setup_routes:
        mock_setup_routes.side_effect = Exception("Failed to setup routes")
        with pytest.raises(Exception):
            agent._HiveAgent__setup_server()


def test_openai_agent_initialization_exception(agent):
    with patch("hive_agent.agent.OpenAIAgent.from_tools") as mock_from_tools:
        mock_from_tools.side_effect = Exception("Failed to initialize OpenAI agent")
        with pytest.raises(Exception):
            agent._HiveAgent__setup()


@pytest.mark.asyncio
async def test_shutdown_procedures_exception(agent):
    with patch("asyncio.gather") as mock_gather:
        mock_gather.side_effect = Exception("Failed to gather tasks")
        with pytest.raises(Exception):
            await agent.shutdown_procedures()


@pytest.mark.asyncio
async def test_cleanup(agent):
    agent.db_session = MagicMock()
    await agent._HiveAgent__cleanup()
    agent.db_session.close.assert_called_once()
