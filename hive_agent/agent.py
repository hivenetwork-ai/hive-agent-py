import asyncio
import logging
import signal
import sys
import uvicorn
import os

from typing import Callable, List, Any, TYPE_CHECKING, Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from llama_index.agent.openai import OpenAIAgent  # type: ignore   # noqa
from llama_index.core.agent import FunctionCallingAgentWorker  # noqa

from hive_agent.llms import OpenAIMultiModalLLM, OpenAILLM, ClaudeLLM, MistralLLM, OllamaLLM

from llama_index.core.llms import ChatMessage
from llama_index.core.tools import FunctionTool

from hive_agent.llm_settings import init_llm_settings
from hive_agent.server.routes import setup_routes, files
from hive_agent.tools.agent_db import get_db_schemas, text_2_sql

from hive_agent.tools.retriever.base_retrieve import RetrieverBase, IndexStore, supported_exts, index_base_dir

from hive_agent.tools.retriever.chroma_retrieve import ChromaRetriever
from hive_agent.tools.retriever.pinecone_retrieve import PineconeRetriever
from llama_index.core.objects import ObjectIndex

from dotenv import load_dotenv
from hive_agent.sdk_context import SDKContext


load_dotenv()


class HiveAgent:
    name: str

    if TYPE_CHECKING:
        from hive_agent.wallet import WalletStore

    wallet_store: "WalletStore"
    __agent: Any

    def __init__(
        self,
        name: str,
        functions: List[Callable],
        config_path="../../hive_config_example.toml",
        host="0.0.0.0",
        port=8000,
        instruction="",
        role="",
        retrieve=False,
        required_exts=None,  # Set default to None and handle in the constructor
        retrieval_tool="basic",
        load_index_file=False,
        sdk_context: Optional[SDKContext] = None
    ):
        self.name = name
        self.functions = functions
        self.config_path = config_path
        self.host = host
        self.port = port
        self.app = FastAPI()
        self.shutdown_event = asyncio.Event()
        self.instruction = instruction
        self.__role__ = role
        self.optional_dependencies: dict[str, bool] = {}
        self.sdk_context = sdk_context if sdk_context is not None else SDKContext(config_path = config_path)
        self.config = self.sdk_context.get_config(name)
        self.retrieve = retrieve
        self.required_exts = supported_exts if required_exts is None else required_exts
        self.retrieval_tool = retrieval_tool
        self.load_index_file = load_index_file
        self.log_level = self.config.get("log", "INFO")
        logging.basicConfig(stream=sys.stdout, level=self.log_level)
        logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

        self.logger = logging.getLogger()
        self.logger.setLevel(self.log_level)

        self._check_optional_dependencies()
        self.__setup()

    def _check_optional_dependencies(self):
        try:
            from web3 import Web3  # noqa

            self.optional_dependencies["web3"] = True
        except ImportError:
            self.optional_dependencies["web3"] = False

    def is_dir_not_empty(self, path):
        if os.path.exists(path):
            if os.path.isfile(path):
                return os.path.getsize(path) > 0
            elif os.path.isdir(path):
                return bool(os.listdir(path))
        return False

    def __setup(self):
        init_llm_settings(self.config)

        self.get_indexstore()
        self.init_agent()

        if self.optional_dependencies.get("web3"):
            from hive_agent.wallet import WalletStore

            self.wallet_store = WalletStore()
            self.wallet_store.add_wallet()
        else:
            self.wallet_store = None
            self.logger.warning("'web3' extras not installed. Web3-related functionality will not be available.")

        self.__setup_server()

    @staticmethod
    def _tools_from_funcs(funcs: List[Callable]) -> List[FunctionTool]:
        return [FunctionTool.from_defaults(fn=func) for func in funcs]

    def __setup_server(self):

        self.configure_cors()
        setup_routes(self.app, self.__agent)

        signal.signal(signal.SIGINT, self.__signal_handler)
        signal.signal(signal.SIGTERM, self.__signal_handler)

    def configure_cors(self):
        environment = self.config.get("environment", "dev")  # default to 'development' if not set

        if environment == "dev":
            logger = logging.getLogger("uvicorn")
            logger.warning("Running in development mode - allowing CORS for all origins")
            self.app.add_middleware(
                CORSMiddleware,
                allow_origins=["*"],
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )

    async def run_server(self):
        try:
            config = uvicorn.Config(app=self.app, host=self.host, port=self.port, loop="asyncio")
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
            index = retriever.create_basic_index()
            self.index_store.add_index(retriever.name, index)

        if "chroma" in self.retrieval_tool:
            chroma_retriever = ChromaRetriever()
            index = chroma_retriever.create_index()
            self.index_store.add_index(chroma_retriever.name, index)

        if "pinecone-serverless" in self.retrieval_tool:
            pinecone_retriever = PineconeRetriever()
            index = pinecone_retriever.create_serverless_index()
            self.index_store.add_index(pinecone_retriever.name, index)

        if "pinecone-pod" in self.retrieval_tool:
            pinecone_retriever = PineconeRetriever()
            index = pinecone_retriever.create_pod_index()
            self.index_store.add_index(pinecone_retriever.name, index)

            self.index_store.save_to_file()

    def get_tools(self):

        custom_tools = self._tools_from_funcs(self.functions)

        # TODO: pass db client to db tools directly
        system_tools = self._tools_from_funcs([get_db_schemas, text_2_sql])

        tools = custom_tools + system_tools

        return tools

    def init_agent(self):
        
        tools = self.get_tools()
        tool_retriever = None

        if self.load_index_file or self.retrieve:
            index_store = IndexStore.get_instance()

            vectorstore_object = ObjectIndex.from_objects(
                tools,
                index=index_store.get_all_indexes(),
            )
            tool_retriever = vectorstore_object.as_retriever(similarity_top_k=3)
            tools = []  # Cannot specify both tools and tool_retriever
            self._assign_agent(tools, tool_retriever)
        else:
            self._assign_agent(tools, tool_retriever)

    def _assign_agent(self, tools, tool_retriever):
        model = self.config.get("model", "gpt-3.5-turbo")

        if model.startswith("gpt-4"):
            agent_class = OpenAIMultiModalLLM
        elif "gpt" in model:
            agent_class = OpenAILLM
        elif "claude" in model:
            agent_class = ClaudeLLM
        elif "llama" in model:
            agent_class = OllamaLLM
        elif "mixtral" in model or "mistral" in model:
            agent_class = MistralLLM
        else:
            agent_class = OpenAILLM

        self.__agent = agent_class(tools, self.instruction, tool_retriever).agent
