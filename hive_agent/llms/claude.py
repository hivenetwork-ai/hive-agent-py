from llama_index.core.settings import Settings
from llama_index.core.agent import FunctionCallingAgentWorker

from hive_agent.llms.llm import LLM


class ClaudeLLM(LLM):
    def __init__(self, llm=None, tools=None, instruction="", tool_retriever=None):
        super().__init__(llm, tools, instruction, tool_retriever)
        print(f"claude tools={tools}")
        self.agent = FunctionCallingAgentWorker.from_tools(
            tools=self.tools if tools is not None else self.tools,
            system_prompt=self.system_prompt,
            # llm=Settings.llm if llm is None else llm,
            llm=llm,
            allow_parallel_tool_calls=False,
            tool_retriever=self.tool_retriever if tool_retriever is not None else self.tool_retriever,
        ).as_agent()
