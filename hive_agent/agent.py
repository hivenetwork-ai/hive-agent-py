import asyncio
import logging
import os
import signal
import sys
import uvicorn

from typing import Callable, List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from llama_index.agent.openai import OpenAIAgent
from llama_index.core.llms import ChatMessage
from llama_index.core.tools import FunctionTool

from hive_agent.llm_settings import init_llm_settings
from hive_agent.server.routes import setup_routes
from hive_agent.wallet import WalletStore

from dotenv import load_dotenv

load_dotenv()

def get_log_level():
    HIVE_AGENT_LOG_LEVEL = os.getenv('HIVE_AGENT_LOG_LEVEL', 'INFO').upper() # Check for env variable on the server and default to INFO if none is provided
    return getattr(logging, HIVE_AGENT_LOG_LEVEL, logging.INFO)

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

logger = logging.getLogger()
logger.setLevel(get_log_level())


class HiveAgent:
    name: str
    wallet_store: WalletStore
    __agent: OpenAIAgent

    def __init__(
            self,
            name: str,
            functions: List[Callable],
            host="0.0.0.0",
            port=8000,
            instruction="",
            db_url="sqlite+aiosqlite:///hive_agent.db"
    ):
        self.name = name
        self.functions = functions
        self.host = host
        self.port = port
        self.app = FastAPI()
        self.shutdown_event = asyncio.Event()
        self.instruction = instruction

        self.__setup(db_url)

    def __setup(self, db_url: str):
        agent_tools = [FunctionTool.from_defaults(fn=func) for func in self.functions]
        self.__agent = OpenAIAgent.from_tools(
            agent_tools,
            system_prompt=f"""You are a domain-specific assistant that is helpful, respectful and honest. Always 
            answer as helpfully as possible, while being safe. Your answers should not include any harmful, 
            unethical, racist, sexist, toxic, dangerous, or illegal content. Please ensure that your responses are 
            socially unbiased and positive in nature. If a question does not make any sense, or is not factually 
            coherent, explain why instead of answering something not correct. If you don't know the answer to a 
            question, please don't share false information.

            You may be provided with tools to help you answer questions. Always ensure you use the result from 
            the most appropriate/relevant function tool to answer the original question in the user's prompt and comment
            on any provided data from the user or from the function result. Whenever you use a tool, explain your answer
            based on the tool result.

            Here is your domain-specific instruction:
            {self.instruction}
            """
        )

        self.wallet_store = WalletStore()
        self.wallet_store.add_wallet()

        self.__setup_server(db_url)

    def __setup_server(self, db_url: str):
        init_llm_settings()

        self.configure_cors()
        setup_routes(self.app, self.__agent, db_url)

        signal.signal(signal.SIGINT, self.__signal_handler)
        signal.signal(signal.SIGTERM, self.__signal_handler)

    def configure_cors(self):
        environment = os.getenv("ENVIRONMENT", "dev")  # default to 'development' if not set

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

    @staticmethod
    def _tools_from_funcs(funcs: List[Callable]) -> List[FunctionTool]:
        return [FunctionTool.from_defaults(fn=func) for func in funcs]

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
            if hasattr(self, 'db_session'):
                await self.db_session.close()
                logging.debug("database connection closed")
        except Exception as e:
            logging.error(f"error during cleanup: {e}", exc_info=True)
        finally:
            logging.info("cleanup process completed")
