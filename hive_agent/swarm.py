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
        llm: Optional[LLM],
        functions: List[Callable],
        agents: List[HiveAgent] = None,
        config_path="../../hive_config_example.toml",
        swarm_id=os.getenv("HIVE_SWARM_ID", ""),
    ):
        self.id = swarm_id
        self.name = name
        self.description = description
        self.instruction = instruction
        self.__agents = AgentMap()
        self.__llm = llm
        self.config = Config(config_path=config_path)
        self.functions = functions

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
            llm=llm_from_wrapper(self.__llm, self.config),
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
