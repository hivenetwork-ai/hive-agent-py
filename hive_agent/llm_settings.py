import toml
from llama_index.llms.openai import OpenAI
from llama_index.core.settings import Settings


def init_llm_settings():
    config = toml.load('../settings.toml')
    model = config.get('model').get('model', 'gpt-3.5-turbo')
    Settings.llm = OpenAI(model=model)
    Settings.chunk_size = 1024
    Settings.chunk_overlap = 20
