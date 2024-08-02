import os
import logging

from dotenv import load_dotenv

load_dotenv()

if "LANGTRACE_API_KEY" in os.environ:
    from langtrace_python_sdk import langtrace

    langtrace.init(api_key=os.getenv("LANGTRACE_API_KEY"))

from llama_index.llms.openai import OpenAI
from llama_index.llms.anthropic import Anthropic
from llama_index.llms.ollama import Ollama
from llama_index.llms.mistralai import MistralAI
from llama_index.core.settings import Settings
from hive_agent.config import Config
from llama_index.multi_modal_llms.openai import OpenAIMultiModal


def init_llm_settings(config):
    model = config.get("model", "model", "gpt-3.5-turbo")
    ollama_server_url = config.get("model", "ollama_server_url", "http://localhost:11434")

    if "gpt-4" in model:  # todo startswith
        Settings.llm = OpenAIMultiModal(model, api_key=os.getenv("OPENAI_API_KEY"), max_new_tokens=300)
    elif "gpt" in model:
        Settings.llm = OpenAI(model=model, request_timeout=config.get("timeout", "llm", 30))
        logging.info("OpenAI model selected")
    elif "claude" in model:
        Settings.llm = Anthropic(model=model, api_key=os.getenv("ANTHROPIC_API_KEY"))
        logging.info("Claude model selected")
    elif "llama" in model:
        Settings.llm = Ollama(
            base_url=ollama_server_url, model="llama3", request_timeout=config.get("timeout", "llm", 30)
        )
        logging.info("Ollama model selected")
    elif "mixtral" or "mistral" in model:
        Settings.llm = MistralAI(model=model, api_key=os.getenv("MISTRAL_API_KEY"))
        logging.info("Mistral model selected")
    else:
        Settings.llm = OpenAI(model=model, request_timeout=config.get("timeout", "llm", 30))
        logging.info("Default OpenAI model selected")

    Settings.chunk_size = 1024
    Settings.chunk_overlap = 20
