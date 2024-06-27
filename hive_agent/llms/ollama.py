from llama_index.core.settings import Settings
from hive_agent.llms.llms import LLMs
from llama_index.core.agent import ReActAgentWorker

class OllamaLLM(LLMs):
    def __init__(self, tools, instruction):
        super().__init__(tools, instruction)
        self.agent = ReActAgentWorker.from_tools(
            tools,
            system_prompt=self.system_prompt,
            llm=Settings.llm,
            verbose=True
        ).as_agent()
