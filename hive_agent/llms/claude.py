from llama_index.core.settings import Settings
from llama_index.core.agent import FunctionCallingAgentWorker

from hive_agent.llms.llms import LLMs


class ClaudeLLM(LLMs):
    def __init__(self, tools, instruction):
        super().__init__(tools, instruction)
        self.agent = FunctionCallingAgentWorker.from_tools(
            tools,
            system_prompt=self.system_prompt,
            llm=Settings.llm,
            allow_parallel_tool_calls=False,
        ).as_agent()

