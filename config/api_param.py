from dotenv import load_dotenv
import os
load_dotenv()

FASTAPI_PORT = int(os.getenv("FASTAPI_PORT"))