from llama_index.core import VectorStoreIndex
from typing import Sequence
from llama_index.core import StorageContext
from system_component.system_logging import Logger
from llama_index.core.schema import BaseNode

class BaseMethodVectorStore():
    def __init__(self):
        # Set vector store
        self._doc_store = None

    def get_doc_store(self):
        # Return vector store
        return self._doc_store

    def build_index_from_nodes(self, nodes: Sequence[BaseNode], embedding_model):
        # Check service
        if self._doc_store == None:
            Logger.exception("Please set vector store")
            raise Exception("Please set vector store")

        # Check input
        assert isinstance(nodes, list), "Please insert list of nodes"
        assert nodes, "Data cannot be empty"

        self._doc_store.add_documents(nodes)
        Logger.info("Building index from documents store")
        # # create storage context
        storage_context = StorageContext.from_defaults(docstore=self._doc_store)
        index = VectorStoreIndex(nodes, storage_context=storage_context,embed_model=embedding_model)
        return index

    def load_index(self, embedding_model):
        # Check service
        if (self._doc_store== None):
            Logger.exception("Please set documents store")
            raise Exception("Please set documents store")

        Logger.info("Loading index from documents store")
        # Build storage context
        storage_context = StorageContext.from_defaults(docstore=self._doc_store)
        return VectorStoreIndex(storage_context=storage_context,embed_model=embedding_model)