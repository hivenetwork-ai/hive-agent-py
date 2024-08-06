import pytest
from unittest.mock import patch
import llama_index
from llama_index.agent.openai import OpenAIAgent  # type: ignore
from hive_agent.llms import OpenAILLM
from hive_agent.llms import OpenAIMultiModalLLM
from hive_agent.llms import ClaudeLLM
from hive_agent.llms import MistralLLM
from hive_agent.llms import OllamaLLM

from llama_index.core.objects import ObjectIndex


@pytest.fixture
def tools():
    return ["tool1", "tool2"]


@pytest.fixture
def instruction():
    return """Act as if you are a financial advisor"""


@pytest.fixture
def empty_tools():
    return []


@pytest.fixture
def required_exts():
    return [".txt", ".md"]


@pytest.fixture
def tool_retriever(tools):
    with patch("llama_index.core.VectorStoreIndex.from_documents"), patch(
        "llama_index.core.objects.ObjectIndex.from_objects"
    ), patch("hive_agent.tools.retriever.base_retrieve.RetrieverBase.create_basic_index") as mock_create_basic_index:
        vectorstore_object = ObjectIndex.from_objects(
            tools,
            index=mock_create_basic_index,
        )
        tool_retriever = vectorstore_object.as_retriever(similarity_top_k=3)
        return tool_retriever


def test_openai_llm_initialization(tools, instruction):
    openai_llm = OpenAILLM(tools, instruction)
    assert openai_llm.agent is not None
    assert isinstance(openai_llm.agent, OpenAIAgent)
    assert openai_llm.tools == tools
    assert instruction in openai_llm.system_prompt


def test_openai_multimodal_llm_initialization(tools, instruction):
    openai_llm = OpenAIMultiModalLLM(tools, instruction)
    assert openai_llm.agent is not None
    assert isinstance(openai_llm.agent, llama_index.core.agent.runner.base.AgentRunner)
    assert openai_llm.tools == tools
    assert instruction in openai_llm.system_prompt


def test_claude_llm_initialization(tools, instruction):
    claude_llm = ClaudeLLM(tools, instruction)
    assert claude_llm.agent is not None
    assert isinstance(claude_llm.agent, llama_index.core.agent.runner.base.AgentRunner)
    assert claude_llm.tools == tools
    assert instruction in claude_llm.system_prompt


def test_llama_llm_initialization(tools, instruction):
    llama_llm = OllamaLLM(tools, instruction)
    assert llama_llm.agent is not None
    assert isinstance(llama_llm.agent, llama_index.core.agent.runner.base.AgentRunner)
    assert llama_llm.tools == tools
    assert instruction in llama_llm.system_prompt


def test_mistral_llm_initialization(tools, instruction):
    mistral_llm = MistralLLM(tools, instruction)
    assert mistral_llm.agent is not None
    assert isinstance(mistral_llm.agent, llama_index.core.agent.runner.base.AgentRunner)
    assert mistral_llm.tools == tools
    assert instruction in mistral_llm.system_prompt


def test_retrieval_openai_llm_initialization(empty_tools, instruction, tool_retriever):
    openai_llm = OpenAILLM(empty_tools, instruction, tool_retriever=tool_retriever)
    assert openai_llm.agent is not None
    assert isinstance(openai_llm.agent, OpenAIAgent)
    assert openai_llm.tools == empty_tools
    assert instruction in openai_llm.system_prompt
    assert openai_llm.tool_retriever == tool_retriever


def test_retrieval_ollamallm_initialization(empty_tools, instruction, tool_retriever):
    ollamallm = OllamaLLM(empty_tools, instruction, tool_retriever=tool_retriever)
    assert ollamallm.agent is not None
    assert isinstance(ollamallm.agent, llama_index.core.agent.runner.base.AgentRunner)
    assert ollamallm.tools == empty_tools
    assert instruction in ollamallm.system_prompt
    assert ollamallm.tool_retriever == tool_retriever
