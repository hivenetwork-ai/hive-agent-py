import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import uuid
from typing import List
from llama_index.core.llms import ChatMessage, MessageRole
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core.agent import ReActAgent

from hive_agent.agent import HiveAgent
from hive_agent.chat import ChatManager
from hive_agent.config import Config
from hive_agent.llms.llm import LLM
from hive_agent.sdk_context import SDKContext
from hive_agent.swarm import HiveSwarm


@pytest.fixture
def mock_sdk_context():
    mock = Mock(spec=SDKContext)
    mock.generate_agents_from_config = Mock(return_value=[])
    mock.add_resource = Mock()
    mock.get_config = Mock(return_value=Mock(spec=Config))
    mock.load_default_utility = AsyncMock()
    mock.get_utility = Mock()
    return mock

@pytest.fixture
def mock_llm():
    llm = MagicMock(spec=LLM)
    # Add any necessary LLM attributes/methods here
    return llm

@pytest.fixture
def mock_functions():
    def dummy_function():
        pass
    return [dummy_function]

@pytest.fixture
def mock_agent():
    agent = MagicMock(spec=HiveAgent)
    agent.name = "test_agent"
    agent.id = str(uuid.uuid4())
    agent.role = "test_role"
    agent.description = "Test agent description"
    agent.metadata = ToolMetadata(name="test_agent", description="Test agent description")
    return agent

@pytest.fixture
def mock_react_agent():
    agent = MagicMock(spec=ReActAgent)
    return agent

@pytest.fixture
def basic_swarm(mock_sdk_context, mock_llm, mock_functions, mock_react_agent):
    with patch('hive_agent.swarm.llm_from_config_without_agent', return_value=mock_llm):
        with patch('hive_agent.swarm.llm_from_wrapper', return_value=mock_llm):
            with patch('hive_agent.swarm.ReActAgent.from_tools', return_value=mock_react_agent):
                swarm = HiveSwarm(
                    name="test_swarm",
                    description="Test swarm",
                    instruction="Test instruction",
                    functions=mock_functions,
                    llm=mock_llm,
                    sdk_context=mock_sdk_context
                )
                return swarm

@pytest.mark.asyncio
async def test_add_agent(basic_swarm, mock_agent, mock_react_agent, mock_llm):
    with patch('hive_agent.swarm.llm_from_wrapper', return_value=mock_llm) as mock_llm_wrapper:
        with patch('hive_agent.swarm.ReActAgent.from_tools', return_value=mock_react_agent):
            mock_llm_wrapper.return_value = mock_llm
            basic_swarm.add_agent(mock_agent)
            assert mock_agent.name in basic_swarm._HiveSwarm__agents
            assert basic_swarm._HiveSwarm__agents[mock_agent.name]["agent"] == mock_agent

@pytest.mark.asyncio
async def test_add_duplicate_agent(basic_swarm, mock_agent, mock_react_agent, mock_llm):
    with patch('hive_agent.swarm.llm_from_wrapper', return_value=mock_llm) as mock_llm_wrapper:
        with patch('hive_agent.swarm.ReActAgent.from_tools', return_value=mock_react_agent):
            mock_llm_wrapper.return_value = mock_llm
            basic_swarm.add_agent(mock_agent)
            with pytest.raises(ValueError, match=f"Agent `{mock_agent.name}` already exists in the swarm."):
                basic_swarm.add_agent(mock_agent)

@pytest.mark.asyncio
async def test_remove_agent(basic_swarm, mock_agent, mock_react_agent, mock_llm):
    with patch('hive_agent.swarm.llm_from_wrapper', return_value=mock_llm) as mock_llm_wrapper:
        with patch('hive_agent.swarm.ReActAgent.from_tools', return_value=mock_react_agent):
            mock_llm_wrapper.return_value = mock_llm
            basic_swarm.add_agent(mock_agent)
            basic_swarm.remove_agent(mock_agent.name)
            assert mock_agent.name not in basic_swarm._HiveSwarm__agents


@pytest.mark.asyncio
async def test_remove_nonexistent_agent(basic_swarm):
    with pytest.raises(ValueError):
        basic_swarm.remove_agent("nonexistent_agent")


@pytest.mark.asyncio
async def test_chat(basic_swarm, mock_sdk_context):
    mock_chat_manager = AsyncMock(spec=ChatManager)
    mock_chat_manager.generate_response = AsyncMock(return_value="Test response")

    with patch('hive_agent.swarm.ChatManager', return_value=mock_chat_manager):
        response = await basic_swarm.chat(
            prompt="Test prompt",
            user_id="test_user",
            session_id="test_session"
        )

        assert response == "Test response"
        mock_chat_manager.generate_response.assert_called_once()


@pytest.mark.asyncio
async def test_chat_history(basic_swarm, mock_sdk_context):
    mock_chat_manager = AsyncMock(spec=ChatManager)
    expected_history = {"messages": [{"role": "user", "content": "Test message"}]}
    mock_chat_manager.get_all_chats_for_user = AsyncMock(return_value=expected_history)

    with patch('hive_agent.swarm.ChatManager', return_value=mock_chat_manager):
        history = await basic_swarm.chat_history(
            user_id="test_user",
            session_id="test_session"
        )

        assert history == expected_history
        mock_chat_manager.get_all_chats_for_user.assert_called_once()


@pytest.mark.asyncio
async def test_format_tool_name(basic_swarm):
    test_cases = [
        ("Test Agent", "test_agent"),
        ("test-agent", "test_agent"),
        ("test.agent!", "testagent"),
        ("Test Agent 123", "test_agent_123"),
    ]

    for input_name, expected_output in test_cases:
        assert basic_swarm._format_tool_name(input_name) == expected_output


@pytest.mark.asyncio
async def test_ensure_utilities_loaded(basic_swarm, mock_sdk_context):
    await basic_swarm._ensure_utilities_loaded()
    mock_sdk_context.load_default_utility.assert_called_once()

    mock_sdk_context.load_default_utility.reset_mock()

    await basic_swarm._ensure_utilities_loaded()
    mock_sdk_context.load_default_utility.assert_not_called()


@pytest.mark.asyncio
async def test_ensure_utilities_loaded_complete(mock_sdk_context, mock_llm, mock_functions, mock_react_agent):
    with patch('hive_agent.swarm.llm_from_config_without_agent', return_value=mock_llm):
        with patch('hive_agent.swarm.llm_from_wrapper', return_value=mock_llm):
            with patch('hive_agent.swarm.ReActAgent.from_tools', return_value=mock_react_agent):
                # Create a fresh swarm instance
                swarm = HiveSwarm(
                    name="test_swarm",
                    description="Test swarm",
                    instruction="Test instruction",
                    functions=mock_functions,
                    llm=mock_llm,
                    sdk_context=mock_sdk_context
                )

                # First call should load utilities
                await swarm._ensure_utilities_loaded()
                mock_sdk_context.load_default_utility.assert_called_once()

                # Reset the mock to clear the call history
                mock_sdk_context.load_default_utility.reset_mock()

                # Second call should not load utilities again
                await swarm._ensure_utilities_loaded()
                mock_sdk_context.load_default_utility.assert_not_called()


@pytest.mark.asyncio
async def test_swarm_with_custom_id(mock_sdk_context, mock_llm, mock_functions, mock_react_agent):
    custom_id = "custom-swarm-id"
    mock_sdk_context.generate_agents_from_config.return_value = []  # Explicitly return empty list

    with patch('hive_agent.swarm.llm_from_config_without_agent', return_value=mock_llm):
        with patch('hive_agent.swarm.llm_from_wrapper', return_value=mock_llm):
            with patch('hive_agent.swarm.ReActAgent.from_tools', return_value=mock_react_agent):
                swarm = HiveSwarm(
                    name="test_swarm",
                    description="Test swarm",
                    instruction="Test instruction",
                    functions=mock_functions,
                    swarm_id=custom_id,
                    sdk_context=mock_sdk_context
                )
                assert swarm.id == custom_id


@pytest.mark.asyncio
async def test_build_swarm_with_agents(mock_sdk_context, mock_llm, mock_agent):
    with patch('hive_agent.swarm.llm_from_config_without_agent', return_value=mock_llm):
        with patch('hive_agent.swarm.llm_from_wrapper', return_value=mock_llm):
            with patch('hive_agent.swarm.ReActAgent.from_tools') as mock_react_agent:
                swarm = HiveSwarm(
                    name="test_swarm",
                    description="Test swarm",
                    instruction="Test instruction",
                    functions=[],
                    sdk_context=mock_sdk_context,
                    llm=mock_llm
                )
                swarm.add_agent(mock_agent)

                mock_react_agent.assert_called()
                call_args = mock_react_agent.call_args[1]
                assert 'tools' in call_args
                assert 'context' in call_args
                assert call_args['context'] == "Test instruction"
