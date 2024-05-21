import toml
import os
from llama_index.llms.openai import OpenAI
from llama_index.core.settings import Settings


def init_llm_settings():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    config_path = os.path.join(dir_path, '..', 'settings.toml')
    config = toml.load(config_path)
    
    model = config.get("model").get("model", "gpt-3.5-turbo")
    Settings.llm = OpenAI(model=model)
    Settings.chunk_size = 1024
    Settings.chunk_overlap = 20
