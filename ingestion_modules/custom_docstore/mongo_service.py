from llama_index.storage.docstore.mongodb import MongoDocumentStore
from ingestion_modules.custom_docstore.base_method_docstore import BaseMethodVectorStore
from typing import Literal,Optional
from config import db_params
from system_component.system_logging import Logger

# Define config
MONGO_DB_NAME = db_params.MONGO_DB_NAME
MONGO_NAME_SPACE = db_params.MONGO_NAME_SPACE
MONGO_PORT = db_params.MONGO_PORT

class MongoService(BaseMethodVectorStore):
    def __init__(self,mongo_uri: Optional[str] = "", port: int = MONGO_PORT,mode : Literal["localhost","cloud"] = "localhost",db_name : str = MONGO_DB_NAME, namespace : str = MONGO_NAME_SPACE):
        super().__init__()
        # Check type
        assert isinstance(db_name,str), "Collection name must be a string"
        # Check type
        assert isinstance(namespace, str), "Namespace name must be a string"
        assert db_name, "DB name can't be empty"
        assert namespace, "Namespace name can't be empty"

        # Define params
        self.uri: str = mode
        self.uri += f":{port}" if mode == "localhost" else mongo_uri
        self.db_name = db_name
        self.namespace = namespace
        self.port = port

        self._doc_store = MongoDocumentStore.from_uri(uri=self.uri,db_name=self.db_name,namespace=self.namespace)
        Logger.info(f"Start Mongo Docstore!")