import logging, sys, os
from datetime import datetime
from typing import Literal

# Define logger
logger = logging.getLogger()
# Define formatter
stdout_log_formatter = logging.Formatter(
    " %(asctime)s | %(filename)s:%(lineno)s | %(levelname)s | %(message)s"
)
# Define handler
stdout_log_handler = logging.StreamHandler(stream=sys.stdout)
stdout_log_handler.setLevel(logging.INFO)
stdout_log_handler.setFormatter(stdout_log_formatter)
logger.addHandler(stdout_log_handler)
# Set level
logger.setLevel(logging.INFO)

current_time = datetime.now().strftime("%d-%m-%y")
log_path = "log"


class Logger:
    @staticmethod
    def info(message: str):
        assert message, "Message cant be None"
        logger.info(message)

    @staticmethod
    def warning(message: str):
        assert message, "Message cant be None"
        logger.warning(message)

    @staticmethod
    def exception(message: str):
        assert message, "Message cant be None"
        logger.exception(message)

    @staticmethod
    def set_log_file(logger, file_path: Literal["chat", "server", "vectorDB"]):
        assert file_path in [
            "chat",
            "server",
            "vectorDB",
        ], "file_path must be 'chat', 'server', or 'vectorDB'"

        # Create log path if not exist
        os.makedirs(f"{log_path}/{file_path}", exist_ok=True)
        file_log_handler = logging.FileHandler(
            f"{log_path}/{file_path}/{current_time}.log", mode="a"
        )
        file_log_handler.setLevel(logging.INFO)
        file_log_handler.setFormatter(stdout_log_formatter)
        logger.addHandler(file_log_handler)