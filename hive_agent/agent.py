import asyncio
import importlib.util
import logging
import signal
import subprocess
import sys
import uvicorn
import os

from typing import Callable, List, Optional, TYPE_CHECKING, Dict

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from llama_index.agent.openai import OpenAIAgent  # type: ignore   # noqa
from llama_index.core.agent import FunctionCallingAgentWorker, AgentRunner  # noqa

from hive_agent.llms.llm import LLM
from hive_agent.llms.openai import OpenAIMultiModalLLM, OpenAILLM
from hive_agent.llms.claude import ClaudeLLM
from hive_agent.llms.mistral import MistralLLM
from hive_agent.llms.ollama import OllamaLLM
from hive_agent.llms.utils import llm_from_config

from llama_index.core.llms import ChatMessage

from hive_agent.server.models import ToolInstallRequest
from hive_agent.server.routes import setup_routes, files
from hive_agent.tools.agent_db import get_db_schemas, text_2_sql

from hive_agent.tools.retriever.base_retrieve import RetrieverBase, IndexStore, supported_exts, index_base_dir

from hive_agent.tools.retriever.chroma_retrieve import ChromaRetriever
from hive_agent.tools.retriever.pinecone_retrieve import PineconeRetriever
from llama_index.core.objects import ObjectIndex
from llama_index.core.tools import QueryEngineTool, ToolMetadata

from dotenv import load_dotenv
from hive_agent.config import Config
from hive_agent.utils import tools_from_funcs

import uuid
from hive_agent.sdk_context import SDKContext

load_dotenv()


class HiveAgent:
    id: str
    name: str

    if TYPE_CHECKING:
        from hive_agent.wallet import WalletStore

    wallet_store: "WalletStore"
    __llm: LLM
    __agent: AgentRunner

    def __init__(
            self,
            name: str,
            functions: List[Callable],
            llm: Optional[LLM] = None,
            config_path="./hive_config_example.toml",
            host="0.0.0.0",
            port=8000,
            instruction="",
            role="",
            description="",
            agent_id=os.getenv("HIVE_AGENT_ID", ""),
            retrieve=False,
            required_exts=supported_exts,
            retrieval_tool="basic",
            load_index_file=False,
            swarm_mode=False,
            sdk_context: Optional[SDKContext] = None
    ):
        self.__llm = llm
        self.id = agent_id if agent_id != "" else str(uuid.uuid4())
        self.name = name
        self.functions = functions
        self.config_path = config_path
        self.__host = host
        self.__port = port
        self.__app = FastAPI()
        self.shutdown_event = asyncio.Event()
        self.instruction = instruction
        self.role = role
        self.description = description
        self.sdk_context = sdk_context if sdk_context is not None else SDKContext(config_path = config_path)
        self.__config = self.sdk_context.get_config(self.id)
        self.__optional_dependencies: dict[str, bool] = {}
        #self.__config = Config(config_path=config_path)
        self.__swarm_mode = swarm_mode
        self.retrieve = retrieve
        self.required_exts = required_exts
        self.retrieval_tool = retrieval_tool
        self.load_index_file = load_index_file
        logging.basicConfig(stream=sys.stdout, level=self.__config.get("log"))
        logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

        self.logger = logging.getLogger()
        self.logger.setLevel(self.__config.get("log"))

        self._check_optional_dependencies()
        self.__setup()

        self.sdk_context.add_resource(self, resource_type="agent")
        [self.sdk_context.add_resource(func, resource_type="tool") for func in self.functions]

    def _check_optional_dependencies(self):
        try:
            from web3 import Web3  # noqa

            self.__optional_dependencies["web3"] = True
        except ImportError:
            self.__optional_dependencies["web3"] = False

    def is_dir_not_empty(self, path):
        if os.path.exists(path):
            if os.path.isfile(path):
                return os.path.getsize(path) > 0
            elif os.path.isdir(path):
                return bool(os.listdir(path))
        return False

    def __setup(self):

        self.get_indexstore()
        self.init_agent()

        if self.__optional_dependencies.get("web3"):
            from hive_agent.wallet import WalletStore

            self.wallet_store = WalletStore()
            self.wallet_store.add_wallet()
        else:
            self.wallet_store = None
            self.logger.warning("'web3' extras not installed. Web3-related functionality will not be available.")

        if self.__swarm_mode is False:
            self.__setup_server()

    def __setup_server(self):

        self.__configure_cors()
        setup_routes(self.__app, self.id, self.sdk_context)

        @self.__app.post("/api/v1/install_tools")
        async def install_tool(tools: List[ToolInstallRequest]):
            try:
                self.install_tools(tools)
                return {"status": "Tools installed successfully"}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        signal.signal(signal.SIGINT, self.__signal_handler)
        signal.signal(signal.SIGTERM, self.__signal_handler)

    def __configure_cors(self):
        environment = self.__config.get("environment")  # default to 'development' if not set

        if environment == "dev":
            logger = logging.getLogger("uvicorn")
            logger.warning("Running in development mode - allowing CORS for all origins")
            self.__app.add_middleware(
                CORSMiddleware,
                allow_origins=["*"],
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )

    async def run_server(self):
        try:
            config = uvicorn.Config(app=self.__app, host=self.__host, port=self.__port, loop="asyncio")
            server = uvicorn.Server(config)
            await server.serve()
        except Exception as e:
            logging.error(f"unexpected error while running the server: {e}", exc_info=True)
        finally:
            await self.__cleanup()

    def run(self):
        try:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(self.run_server())
        except Exception as e:
            logging.error(f"An error occurred in the main event loop: {e}", exc_info=True)

    def chat_history(self) -> List[ChatMessage]:
        return self.__agent.chat_history

    def query(self, *args, **kwargs):
        return self.__agent.query(*args, **kwargs)

    def aquery(self, *args, **kwargs):
        return self.__agent.aquery(*args, **kwargs)

    def __signal_handler(self, signum, frame):
        logging.info(f"signal {signum} received, initiating graceful shutdown...")
        asyncio.create_task(self.shutdown_procedures())

    async def shutdown_procedures(self):
        # attempt to complete or cancel all running tasks
        tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
        [task.cancel() for task in tasks]

        await asyncio.gather(*tasks, return_exceptions=True)
        self.shutdown_event.set()
        logging.info("all tasks have been cancelled or completed")

    async def __cleanup(self):
        try:
            if hasattr(self, "db_session"):
                await self.db_session.close()
                logging.debug("database connection closed")
        except Exception as e:
            logging.error(f"error during cleanup: {e}", exc_info=True)
        finally:
            logging.info("cleanup process completed")

    def get_indexstore(self):
        is_base_dir_not_empty = self.is_dir_not_empty(files.BASE_DIR)
        is_index_dir_not_empty = self.is_dir_not_empty(index_base_dir)

        if is_index_dir_not_empty and self.load_index_file:
            self.index_store = IndexStore.load_from_file()
        else:
            self.index_store = IndexStore.get_instance()
        
        if is_base_dir_not_empty and self.retrieve:
            self.add_batch_indexes()

    def add_batch_indexes(self):
    
        if "basic" in self.retrieval_tool:
            retriever = RetrieverBase()
            index,file_names = retriever.create_basic_index()
            self.index_store.add_index(retriever.name, index, file_names)

        if "chroma" in self.retrieval_tool:
            chroma_retriever = ChromaRetriever()
            index,file_names = chroma_retriever.create_index()
            self.index_store.add_index(chroma_retriever.name, index, file_names)

        if "pinecone-serverless" in self.retrieval_tool:
            pinecone_retriever = PineconeRetriever()
            index,file_names = pinecone_retriever.create_serverless_index()
            self.index_store.add_index(pinecone_retriever.name, index, file_names)

        if "pinecone-pod" in self.retrieval_tool:
            pinecone_retriever = PineconeRetriever()
            index,file_names = pinecone_retriever.create_pod_index()
            self.index_store.add_index(pinecone_retriever.name, index, file_names)

            self.index_store.save_to_file()

    def get_tools(self):

        custom_tools = tools_from_funcs(self.functions)
        
        self.sdk_context.load_default_utility()

        def _text_2_sql(query: str):
            return text_2_sql(self.sdk_context, query)
        
        def _get_db_schemas():
            return get_db_schemas(self.sdk_context)
        
        system_tools = tools_from_funcs([
            _text_2_sql,
            _get_db_schemas
        ])
        tools = custom_tools + system_tools

        return tools

    def init_agent(self):

        tools = self.get_tools()
        tool_retriever = None

        if self.load_index_file or self.retrieve or len(self.index_store.list_indexes()) > 0:
            index_store = IndexStore.get_instance()
            query_engine_tools = []
            for index_name in index_store.get_all_index_names():
                index_files = index_store.get_index_files(index_name)
                query_engine_tools.append(
                    QueryEngineTool(
                        query_engine = index_store.get_index(index_name).as_query_engine(),
                        metadata=ToolMetadata(name=index_name+'_tool',
                                              description=("Useful for questions related to specific aspects of documents"
                                              f" {index_files}")
                                                                                                            )))
            
            tools = tools + query_engine_tools

            vectorstore_object = ObjectIndex.from_objects(
                tools,
                index=index_store.get_all_indexes(),
            )
            tool_retriever = vectorstore_object.as_retriever(similarity_top_k=3)
            tools = []  # Cannot specify both tools and tool_retriever
            self._assign_agent(tools, tool_retriever)
        else:
            self._assign_agent(tools, tool_retriever)
    
    def recreate_agent(self):
        return self.init_agent()

    def _assign_agent(self, tools, tool_retriever):
        if self.__llm is not None:
            print(f"using provided llm: {type(self.__llm)}")
            self.__agent = self.__llm.agent
        else:
            model = self.__config.get("model")
            enable_multi_modal = self.__config.get("enable_multi_modal")
            llm = llm_from_config(self.__config)

            if model.startswith("gpt-4") and enable_multi_modal is True:
                agent_class = OpenAIMultiModalLLM
            elif "gpt" in model:
                agent_class = OpenAILLM
            elif "claude" in model:
                agent_class = ClaudeLLM
            elif "llama" in model:
                agent_class = OllamaLLM
            elif "mixtral" in model or "mistral" in model or "codestral" in model:
                agent_class = MistralLLM
            else:
                agent_class = OpenAILLM

            self.sdk_context.set_attributes(
                id=self.id,
                llm = llm,
                tools=tools,
                tool_retriever=tool_retriever,
                agent_class=agent_class,
                instruction=self.instruction
            )

            self.__agent = agent_class(llm, tools, self.instruction, tool_retriever).agent

    def add_tool(self, function_tool):
        self.functions.append(function_tool)
        self.recreate_agent()

    def install_tools(self, tools: List[ToolInstallRequest], install_path="/tmp"):
        """
        Install tools from a list of tool configurations.

        :param install_path: Path to the folder where the tools are installed
        :param tools: List of dictionaries where each dictionary has:
                      - 'url': the GitHub URL of the tool repository.
                      - 'functions': list of paths to the functions to import.
        """
        for tool in tools:
            url = tool.url
            functions = tool.functions
            tool_install_path = install_path
            if tool.install_path is not None:
                tool_install_path = tool.install_path

            repo_dir = os.path.join(tool_install_path, os.path.basename(url))
            if not os.path.exists(repo_dir):
                subprocess.run(["git", "clone", url, repo_dir], check=True)

            for func_path in functions:
                module_name, func_name = func_path.rsplit(".", 1)
                module_path = os.path.join(repo_dir, *module_name.split(".")) + ".py"

                spec = importlib.util.spec_from_file_location(module_name, module_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                func = getattr(module, func_name)
                self.functions.append(func)
                print(f"Installed function: {func_name} from {module_name}")

        self.recreate_agent()
    
