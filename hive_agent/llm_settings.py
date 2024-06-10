import os
import logging

from langtrace_python_sdk import langtrace
langtrace.init(api_key = '37ff4185b3d32a171fdbaa286ac8fdb0aac11e5c797f150e4a687fab0aff0c5b')

from llama_index.llms.openai import OpenAI
from llama_index.llms.anthropic import Anthropic
from llama_index.llms.ollama import Ollama
from llama_index.llms.mistralai import MistralAI
from llama_index.core.settings import Settings
from hive_agent.config import Config
from dotenv import load_dotenv
load_dotenv()

def init_llm_settings():
    config = Config()
    model = config.get("model", "model", "gpt-3.5-turbo")
    if "gpt" in model:
        Settings.llm = OpenAI(model=model) 
        logging.info(f"Model selected is openai")
    elif "claude" in model: 
        Settings.llm = Anthropic(model=model, api_key=os.getenv('ANTHROPIC_API_KEY'))
        logging.info(f"Model selected is Claude")
    elif "llama" in model:
        Settings.llm = Ollama(model=model, api_key=os.getenv('LLAMA_API_KEY'))
        logging.info(f"Model selected is Llama")
    elif "mixtral" or "mistral" in model:
        Settings.llm = MistralAI(model=model, api_key=os.getenv('MISTRAL_API_KEY'))
        logging.info(f"Model selected is Mistral")
    else:
        logging.info(f"Model selected is default")

    Settings.chunk_size = 1024
    Settings.chunk_overlap = 20