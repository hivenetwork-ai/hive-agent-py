import os
import string
from typing import List, Dict, Any, Optional, Callable

from llama_index.core.agent import AgentRunner, ReActAgent
from llama_index.core.tools import QueryEngineTool, ToolMetadata

from hive_agent.agent import HiveAgent
from hive_agent.config import Config
from hive_agent.llms.llm import LLM
from hive_agent.llms.utils import llm_from_wrapper
from hive_agent.utils import tools_from_funcs
from hive_agent.sdk_context import SDKContext
from hive_agent.llms.utils import llm_from_config_without_agent

import uuid

class AgentMap(Dict[str, Dict[str, Any]]):
    def __init__(self):
        super().__init__()


class HiveSwarm:
    id: str
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
        functions: List[Callable],
        llm: Optional[LLM] = None,
        agents: List[HiveAgent] = None,
        config_path="./hive_config_example.toml",
        swarm_id=os.getenv("HIVE_SWARM_ID", ""),
        sdk_context: Optional[SDKContext] = None
    ):
        self.id = swarm_id if swarm_id != "" else str(uuid.uuid4())
        self.name = name
        self.description = description
        self.instruction = instruction
        self.__agents = AgentMap()
        self.functions = functions
        self.sdk_context = sdk_context if sdk_context is not None else SDKContext(config_path=config_path)
        self.__config = self.sdk_context.get_config(self.name)
        self.__llm = llm if llm is not None else llm_from_config_without_agent(self.__config)


        agents = self.sdk_context.generate_agents_from_config()
        if agents:
            for agent in agents:
                self.__agents[agent.name] = {
                    "id": agent.id,
                    "agent": agent,
                    "role": agent.role,
                    "description": agent.description,
                    "sdk_context": self.sdk_context
                }
                
        self.sdk_context.add_resource(self, resource_type="swarm")
        self._build_swarm()

    def _build_swarm(self):
        query_engine_tools = (
            [
                QueryEngineTool(
                    query_engine=agent_data["agent"],
                    metadata=ToolMetadata(
                        name=self._format_tool_name(agent_name),
                        description=agent_data["description"],
                    ),
                )
                for agent_name, agent_data in self.__agents.items()
            ]
            if self.__agents
            else []
        )

        custom_tools = tools_from_funcs(funcs=self.functions)
        tools = custom_tools + query_engine_tools

        self.__swarm = ReActAgent.from_tools(
            tools=tools,
            llm=llm_from_wrapper(self.__llm, self.__config),
            verbose=True,
            context=self.instruction,
        )

    def add_agent(self, agent: HiveAgent):
        if agent.name in self.__agents:
            raise ValueError(f"Agent `{agent.name}` already exists in the swarm.")
        self.__agents[agent.name] = {
            "id": agent.id,
            "agent": agent,
            "role": agent.role,
            "description": agent.description,
        }
        self.sdk_context.add_resource(agent, resource_type="agent")
        self._build_swarm()

    def remove_agent(self, name: str):
        if name not in self.__agents:
            raise ValueError(f"Agent `{name}` does not exist in the swarm.")
        del self.__agents[name]
        self._build_swarm()

    async def chat(self, prompt):
        response = await self.__swarm.achat(
            message=prompt
        )
        return response

    def chat_history(self):
        return self.__swarm.chat_history

    def _format_tool_name(self, name: str) -> str:
        tmp = name.replace(" ", "_").replace("-", "_").lower()
        exclude = string.punctuation.replace("_", "")
        translation_table = str.maketrans("", "", exclude)
        result = tmp.translate(translation_table)

        return result
