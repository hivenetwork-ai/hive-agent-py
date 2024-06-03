import os
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
    elif "claude" in model: 
        Settings.llm = Anthropic(model=model, api_key=os.getenv('ANTHROPIC_API_KEY'))
    elif "mixtral" in model:
        Settings.llm = MistralAI(model=model, api_key=os.getenv('MISTRAL_API_KEY'))
    elif "llama" in model:
        Settings.llm = Ollama(model=model, api_key=os.getenv('LLAMA_API_KEY'))
    else:
        Settings.llm = OpenAI(model=model)

    Settings.chunk_size = 1024
    Settings.chunk_overlap = 20