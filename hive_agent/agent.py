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

from hive_agent.routes import setup_routes
from hive_agent.llm_settings import init_llm_settings
from hive_agent.wallet import WalletStore

load_dotenv()

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))


class HiveAgent:
    name: str
    wallet_store: WalletStore

    __agent: OpenAIAgent

    def __init__(self, name: str, functions: List[Callable], host="0.0.0.0", port=8000):
        self.name = name
        self.functions = functions
        self.host = host
        self.port = port
        self.app = FastAPI()
        self.shutdown_event = Event()

        self.__setup()

    def __setup(self):
        agent_tools = [FunctionTool.from_defaults(fn=func) for func in self.functions]
        self.__agent = OpenAIAgent.from_tools(agent_tools)
        self.wallet_store = WalletStore()
        self.wallet_store.add_wallet()

        self.__setup_server()

    def __setup_server(self):
        init_llm_settings()

        self.configure_cors()
        setup_routes(self.app, self.__agent)

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
        # TODO: implement cleanup and resource release logic
