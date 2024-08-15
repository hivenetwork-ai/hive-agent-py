from llama_index.core.settings import Settings
from llama_index.agent.openai import OpenAIAgent
from hive_agent.llms.llm import LLM


class OpenAILLM(LLM):
    def __init__(self, llm=None, tools=None, instruction="", tool_retriever=None):
        super().__init__(llm, tools, instruction, tool_retriever)
        # print(f"inside OpenAILLM, Settings.llm is {Settings.llm}")
        print(f"inside OpenAILLM, llm is {llm}")
        self.agent = OpenAIAgent.from_tools(
            # llm=Settings.llm if llm is None else llm,
            llm=llm,
            tools=self.tools if tools is not None else self.tools,
            system_prompt=self.system_prompt,
            tool_retriever=self.tool_retriever if tool_retriever is not None else self.tool_retriever,
        )
