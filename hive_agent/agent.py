import logging
import os
import signal
import sys
import uvicorn

from threading import Thread, Event
from typing import Callable, List

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from llama_index.agent.openai import OpenAIAgent
from llama_index.core.llms import ChatMessage
from llama_index.core.tools import FunctionTool

from hive_agent.server.routes import setup_routes
from hive_agent.llm_settings import init_llm_settings
from hive_agent.wallet import WalletStore

load_dotenv()

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))


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
        self.shutdown_event = Event()
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

    def run_server(self):
        try:
            uvicorn.run(app=self.app, host=self.host, port=self.port)
        except Exception as e:
            logging.error(f"server error: {e}")
        finally:
            self.shutdown_event.set()
            self.__cleanup()

    def run(self):
        thread = Thread(target=self.run_server)
        thread.daemon = True
        thread.start()
        self.shutdown_event.wait()

    def chat_history(self) -> List[ChatMessage]:
        return self.__agent.chat_history

    @staticmethod
    def _tools_from_funcs(funcs: List[Callable]) -> List[FunctionTool]:
        return [FunctionTool.from_defaults(fn=func) for func in funcs]

    def __signal_handler(self, signum, frame):
        logging.debug("signal received, shutting down...")
        self.shutdown_event.set()

    def __cleanup(self):
        logging.debug("performing cleanup...")

        # close database connections
        if hasattr(self, 'db_session'):
            self.db_session.close()
            logging.debug("Database connection closed")

        logging.debug("cleanup completed successfully")
