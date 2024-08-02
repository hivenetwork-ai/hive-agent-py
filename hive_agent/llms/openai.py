from llama_index.agent.openai import OpenAIAgent
from llama_index.core.agent.react_multimodal.step import MultimodalReActAgentWorker
from hive_agent.llms.llms import LLMs
from llama_index.core.settings import Settings
from llama_index.core.agent import Task


class OpenAILLM(LLMs):
    def __init__(self, tools, instruction, tool_retriever=None):
        super().__init__(tools, instruction, tool_retriever)
        self.agent = OpenAIAgent.from_tools(
            tools=self.tools,
            system_prompt=self.system_prompt,
            tool_retriever=tool_retriever,
        )


class OpenAIMultiModalLLM(LLMs):
    def __init__(self, tools, instruction, tool_retriever=None):
        super().__init__(tools, instruction, tool_retriever)
        self.agent = MultimodalReActAgentWorker.from_tools(
            tools=self.tools,
            system_prompt=self.system_prompt,
            tool_retriever=tool_retriever,
            multi_modal_llm=Settings.llm,
        ).as_agent()
