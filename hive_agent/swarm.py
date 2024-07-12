from typing import List, Dict, Any, Optional

from llama_index.core.agent import (
    AgentRunner,
    ReActAgentWorker,
    StructuredPlannerAgent,
    ReActAgent,
)
from llama_index.core import PromptTemplate
from llama_index.core.llms import ChatMessage, MessageRole
from llama_index.core.tools import QueryEngineTool, ToolMetadata

from hive_agent import HiveAgent
from hive_agent.config import Config
from hive_agent.llms import LLM
from hive_agent.llms.utils import init_llm_settings, llm_from_wrapper


class AgentMap(Dict[str, Dict[str, Any]]):
    def __init__(self):
        super().__init__()


class HiveSwarm:
    name: str
    instruction: str
    description: str
    __llm: LLM
    __agents: AgentMap
    __swarm: AgentRunner

    def __init__(
        self,
        name: str,
        description: str,
        instruction: str,
        llm: Optional[LLM],
        agents: List[HiveAgent] = None,
        config_path="../../hive_config_example.toml",
    ):
        self.name = name
        self.description = description
        self.instruction = instruction
        self.__agents = AgentMap()
        self.__llm = llm
        self.config = Config(config_path=config_path)
        init_llm_settings(self.config)

        if agents:
            for agent in agents:
                self.__agents[agent.name] = {
                    "id": agent.id,
                    "agent": agent,
                    "role": agent.role,
                    "description": agent.description,
                }

        self._build_swarm()

    def _build_swarm(self):
        query_engine_tools = [
            QueryEngineTool(
                query_engine=agent_data["agent"],
                metadata=ToolMetadata(
                    name=agent_name, description=agent_data["description"]
                ),
            )
            for agent_name, agent_data in self.__agents.items()
        ]
        self.__swarm = ReActAgent.from_tools(
            tools=query_engine_tools,
            llm=llm_from_wrapper(self.__llm, self.config),
            verbose=True,
            context=self.instruction,
        )

        # worker = ReActAgentWorker(
        #     tools=query_engine_tools, llm=llm_from_wrapper(self.__llm), verbose=True
        # )
        # # print(worker.get_prompts())
        # system_prompt = self._get_system_prompt()
        # worker.update_prompts({"system_prompt": system_prompt})
        #
        # self.__swarm = StructuredPlannerAgent(
        #     worker, tools=query_engine_tools, verbose=True
        # )

    def _get_system_prompt(self):
        react_system_header_str = (
            """\
    
            You are designed to help with a variety of tasks, from answering questions \
                to providing summaries to other types of analyses.
                
            Here is your overall instruction that encompasses the tasks you will be solving:
            """
            + self.instruction
            + """\
            
            ## Tools
            You have access to a wide variety of tools. You are responsible for using
            the tools in any sequence you deem appropriate to complete the task at hand.
            This may require breaking the task into subtasks and using different tools
            to complete each subtask.
    
            You have access to the following tools:
            {tool_desc}
    
            ## Output Format
            To answer the question, please use the following format.
    
            ```
            Thought: I need to use a tool to help me answer the question.
            Action: tool name (one of {tool_names}) if using a tool.
            Action Input: the input to the tool, in a JSON format representing the kwargs (e.g. {{"input": "hello world", "num_beams": 5}})
            ```
    
            Please ALWAYS start with a Thought.
    
            Please use a valid JSON format for the Action Input. Do NOT do this {{'input': 'hello world', 'num_beams': 5}}.
    
            If this format is used, the user will respond in the following format:
    
            ```
            Observation: tool response
            ```
    
            You should keep repeating the above format until you have enough information
            to answer the question without using any more tools. At that point, you MUST respond
            in the one of the following two formats:
    
            ```
            Thought: I can answer without using any more tools.
            Answer: [your answer here]
            ```
    
            ```
            Thought: I cannot answer the question with the provided tools.
            Answer: Sorry, I cannot answer your query.
            ```
    
            ## Additional Rules
            - The answer MUST contain a sequence of bullet points that explain how you arrived at the answer. This can include aspects of the previous conversation history.
            - You MUST obey the function signature of each tool. Do NOT pass in no arguments if the function expects arguments.
    
            ## Current Conversation
            Below is the current conversation consisting of interleaving human and assistant messages.
    
            """
        )

        system_prompt = PromptTemplate(react_system_header_str)

        return system_prompt

    def add_agent(self, agent: HiveAgent):
        if agent.name in self.__agents:
            raise ValueError(f"Agent `{agent.name}` already exists in the swarm.")
        self.__agents[agent.name] = {
            "id": agent.id,
            "agent": agent,
            "role": agent.role,
            "description": agent.description,
        }
        self._build_swarm()

    def remove_agent(self, name: str):
        if name not in self.__agents:
            raise ValueError(f"Agent `{name}` does not exist in the swarm.")
        del self.__agents[name]
        self._build_swarm()

    async def chat(self, prompt):
        # message = ChatMessage(role=MessageRole.USER, content=prompt)
        # self.chat_history().append(message)
        response = await self.__swarm.achat(
            message=prompt  # , chat_history=self.chat_history()
        )
        # self.chat_history().append(response)
        return response

    def chat_history(self):
        return self.__swarm.chat_history
