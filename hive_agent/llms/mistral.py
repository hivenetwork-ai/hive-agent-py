from llama_index.core.settings import Settings
from llama_index.core.agent import FunctionCallingAgentWorker

from hive_agent.llms.llm import LLM


class MistralLLM(LLM):
    def __init__(self, tools=None, instruction="", tool_retriever=None):
        super().__init__(tools, instruction, tool_retriever)
        print(f"inside {MistralLLM}: Settings.llm is {Settings.llm}")
        self.agent = FunctionCallingAgentWorker.from_tools(
            tools,
            system_prompt=self.system_prompt,
            llm=Settings.llm,
            allow_parallel_tool_calls=False,
            tool_retriever=tool_retriever,
        ).as_agent()
