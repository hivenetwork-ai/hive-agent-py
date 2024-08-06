from llama_index.core.settings import Settings
from llama_index.agent.openai import OpenAIAgent
from hive_agent.llms.llm import LLM


class OpenAILLM(LLM):
    def __init__(self, tools=None, instruction="", tool_retriever=None):
        super().__init__(tools, instruction, tool_retriever)
        print(f"inside OpenAILLM, Settings.llm is {Settings.llm}")
        self.agent = OpenAIAgent.from_tools(
            llm=Settings.llm,
            tools=self.tools,
            system_prompt=self.system_prompt,
            tool_retriever=tool_retriever,
        )
