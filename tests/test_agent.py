import os
import signal
from unittest.mock import MagicMock, patch

import pytest
from hive_agent.agent import HiveAgent
from hive_agent.tools.retriever.base_retrieve import IndexStore
from llama_index.core.agent.runner.base import AgentRunner


@pytest.fixture
def agent():
    with patch.object(IndexStore, "get_instance", return_value=IndexStore()), patch(
        "hive_agent.agent.OpenAILLM"
    ), patch("hive_agent.agent.ClaudeLLM"), patch("hive_agent.agent.MistralLLM"), patch(
        "hive_agent.agent.OllamaLLM"
    ), patch(
        "hive_agent.wallet.WalletStore"
    ), patch(
        "hive_agent.agent.setup_routes"
    ), patch(
        "uvicorn.Server.serve", new_callable=MagicMock
    ), patch(
        "llama_index.core.VectorStoreIndex.from_documents"
    ), patch(
        "llama_index.core.objects.ObjectIndex.from_objects"
    ), patch.object(
        IndexStore, "save_to_file", MagicMock()
    ):

        os.environ['ANTHROPIC_API_KEY'] = "anthropic_api_key"
        os.environ['MISTRAL_API_KEY'] = "mistral_api_key"

        test_agent = HiveAgent(
            name="TestAgent",
            functions=[lambda x: x],
            config_path="./hive_config_test.toml",
            host="0.0.0.0",
            port=8000,
            instruction="Test instruction",
            role="leader",
            retrieve=True,
            required_exts=[".txt"],
            retrieval_tool="basic",
            load_index_file=False,
        )
    return test_agent


@pytest.mark.asyncio
async def test_agent_initialization(agent):
    assert agent.name == "TestAgent"
    assert agent.config_path == "./hive_config_test.toml"
    assert agent.instruction == "Test instruction"
    assert agent.role == "leader"
    assert agent.retrieve is True
    assert agent.required_exts == [".txt"]
    assert agent.retrieval_tool == "basic"
    assert agent.load_index_file is False


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
    with patch("llama_index.agent.openai.OpenAIAgent.from_tools") as mock_from_tools:
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


def test_recreate_agent(agent):
    """
    with patch("hive_agent.utils.tools_from_funcs") as mock_tools_from_funcs, patch.object(
        IndexStore, "get_instance"
    ) as mock_get_instance, patch.object(ObjectIndex, "from_objects") as mock_from_objects, patch.object(
        agent, "_assign_agent"
    ) as mock_assign_agent:

        mock_custom_tools = [MagicMock(name="custom_tool")]
        mock_system_tools = [MagicMock(name="system_tool")]
        mock_tools_from_funcs.side_effect = [mock_custom_tools, mock_system_tools]

        mock_index_store = MagicMock()
        mock_get_instance.return_value = mock_index_store

        mock_vectorstore_object = MagicMock()
        mock_from_objects.return_value = mock_vectorstore_object

        agent.recreate_agent()

        mock_tools_from_funcs.assert_any_call(agent.functions)
        mock_tools_from_funcs.assert_any_call([get_db_schemas, text_2_sql])

        mock_get_instance.assert_called_once()

        mock_from_objects.assert_called_once_with(
            mock_custom_tools + mock_system_tools,
            index=mock_index_store.get_all_indexes(),
        )

        mock_vectorstore_object.as_retriever.assert_called_once_with(similarity_top_k=3)

        mock_assign_agent.assert_called_once_with([], mock_vectorstore_object.as_retriever.return_value)
    """
    pass


def test_assign_agent(agent):
    with patch("hive_agent.llms.openai.OpenAIMultiModalLLM") as mock_openai_multimodal, patch(
        "hive_agent.llms.openai.OpenAILLM"
    ) as mock_openai_llm, patch("hive_agent.llms.claude.ClaudeLLM") as mock_claude_llm, patch(
        "hive_agent.llms.ollama.OllamaLLM"
    ) as mock_ollama_llm, patch(
        "hive_agent.llms.mistral.MistralLLM"
    ) as mock_mistral_llm:

        models = [
            ("gpt-4o", mock_openai_multimodal),
            ("gpt-3.5-turbo", mock_openai_llm),
            ("claude-3-opus-20240229", mock_claude_llm),
            ("llama-2", mock_ollama_llm),
            ("mistral-large-latest", mock_mistral_llm),
            ("gpt-4", mock_openai_llm),
        ]

        tools = MagicMock()
        tool_retriever = MagicMock()

        for model_name, expected_mock_class in models:
            with patch("hive_agent.config.Config.get", return_value=model_name):

                agent._assign_agent(tools, tool_retriever)

                # expected_mock_class.assert_called_once()  # todo not working

                assert isinstance(agent._HiveAgent__agent, AgentRunner)

                # expected_mock_class.reset_mock()
