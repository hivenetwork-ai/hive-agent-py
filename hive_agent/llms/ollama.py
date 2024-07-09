from llama_index.core.settings import Settings
from hive_agent.llms.llms import LLMs
from llama_index.core.agent import ReActAgentWorker


class OllamaLLM(LLMs):
    def __init__(self, tools, instruction, tool_retriever=None):
        super().__init__(tools, instruction, tool_retriever)
        self.agent = ReActAgentWorker.from_tools(
            tools,
            system_prompt=self.system_prompt,
            llm=Settings.llm,
            verbose=True,
            tool_retriever=tool_retriever,
        ).as_agent()
