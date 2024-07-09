from llama_index.agent.openai import OpenAIAgent
from hive_agent.llms.llms import LLMs


class OpenAILLM(LLMs):
    def __init__(self, tools, instruction,tool_retriever=None):
        super().__init__(tools, instruction,tool_retriever)
        self.agent = OpenAIAgent.from_tools(
            tools=self.tools, system_prompt=self.system_prompt, tool_retriever = tool_retriever
        )
