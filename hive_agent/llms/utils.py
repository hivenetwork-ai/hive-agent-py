import os
import logging
from typing import Optional
from dotenv import load_dotenv

if "LANGTRACE_API_KEY" in os.environ:
    from langtrace_python_sdk import langtrace

    langtrace.init(api_key=os.getenv("LANGTRACE_API_KEY"))

from .llm import LLM
from .claude import ClaudeLLM
from .mistral import MistralLLM
from .ollama import OllamaLLM
from .openai import OpenAILLM
from hive_agent.config import Config

from llama_index.llms.openai import OpenAI
from llama_index.llms.anthropic import Anthropic
from llama_index.llms.ollama import Ollama
from llama_index.llms.mistralai import MistralAI
from llama_index.core.settings import Settings

load_dotenv()

DEFAULT_LLM_TIMEOUT = 30

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_llm(model: str, llm_type: str, timeout: int = DEFAULT_LLM_TIMEOUT):
    if llm_type == "OpenAI":
        return OpenAI(model=model, timeout=timeout)
    elif llm_type == "Anthropic":
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            logger.error("ANTHROPIC_API_KEY is missing")
            raise ValueError("ANTHROPIC_API_KEY is required for Anthropic models")
        return Anthropic(model=model, api_key=api_key)
    elif llm_type == "Ollama":
        return Ollama(model=model, timeout=timeout)
    elif llm_type == "Mistral":
        api_key = os.getenv("MISTRAL_API_KEY")
        if not api_key:
            logger.error("MISTRAL_API_KEY is missing")
            raise ValueError("MISTRAL_API_KEY is required for Mistral models")
        return MistralAI(model=model, api_key=api_key)
    else:
        logger.error("Unsupported LLM type")
        raise ValueError("Unsupported LLM type")


def llm_from_wrapper(llm_wrapper: LLM):
    model = os.getenv("MODEL")
    if isinstance(llm_wrapper, OpenAILLM):
        return create_llm(model, "OpenAI")
    elif isinstance(llm_wrapper, ClaudeLLM):
        return create_llm(model, "Anthropic")
    elif isinstance(llm_wrapper, OllamaLLM):
        return create_llm(model, "Ollama")
    elif isinstance(llm_wrapper, MistralLLM):
        return create_llm(model, "Mistral")
    else:
        logger.error("Unsupported LLM wrapper type")
        raise ValueError("Unsupported LLM wrapper type")


def _get_llm(model, config: Optional[Config]):
    timeout = (
        config.get("timeout", "llm", DEFAULT_LLM_TIMEOUT)
        if config
        else DEFAULT_LLM_TIMEOUT
    )

    if "gpt" in model:
        logger.info("OpenAI model selected")
        return create_llm(model, "OpenAI", timeout)
    elif "claude" in model:
        logger.info("Claude model selected")
        return create_llm(model, "Anthropic", timeout)
    elif "llama" in model:
        logger.info("Llama model selected")
        return create_llm(model, "Ollama", timeout)
    elif any(keyword in model for keyword in ["mixtral", "mistral", "codestral"]):
        logger.info("Mistral model selected")
        return create_llm(model, "Mistral", timeout)
    else:
        logger.info("Default OpenAI model selected")
        return create_llm(model, "OpenAI", timeout)


def init_llm_settings(config: Config):
    model = config.get("model", "model", "gpt-3.5-turbo")
    Settings.llm = _get_llm(model, config)
    Settings.chunk_size = 1024
    Settings.chunk_overlap = 20
    logger.info("LLM settings initialized")
