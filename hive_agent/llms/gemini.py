from hive_agent.llms.llm import LLM
from llama_index.core.agent import ReActAgentWorker

class GeminiLLM(LLM):
    def __init__(self, llm=None, tools=None, instruction="", tool_retriever=None):
        super().__init__(llm, tools, instruction, tool_retriever)
        self.agent = ReActAgentWorker.from_tools(
            tools=self.tools,
            system_prompt=self.system_prompt,
            llm=self.llm, 
            allow_parallel_tool_calls=False,
            tool_retriever=self.tool_retriever,
        ).as_agent()