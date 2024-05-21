from llama_index.llms.openai import OpenAI
from llama_index.core.settings import Settings
from hive_agent.config import Config


def init_llm_settings():
    config = Config()
    model = config.get("model", "model", "gpt-3.5-turbo")
    Settings.llm = OpenAI(model=model)
    Settings.chunk_size = 1024
    Settings.chunk_overlap = 20
