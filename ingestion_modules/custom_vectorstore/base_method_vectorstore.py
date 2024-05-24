from llama_index.core import VectorStoreIndex
from llama_index.core.schema import Document, BaseNode
from typing import List, Literal
from llama_index.core import StorageContext
from system_component.system_logging import Logger


class BaseMethodVectorStore:
    def __init__(self, vector_store=None):
        # Set vector store
        self._vector_store = vector_store

    def get_vector_store(self):
        # Return vector store
        return self._vector_store

    def build_index_from_docs(self, documents: List[Document], embedding_model):
        # Check service
        if self._vector_store == None:
            Logger.exception("Please set vector store")
            raise Exception("Please set vector store")

        # Check input
        assert isinstance(documents, list), "Please insert list of documents"
        assert documents, "Data cannot be empty"

        # Build storage context
        storage_context = StorageContext.from_defaults(vector_store=self._vector_store)
        # Update state
        Logger.info("Building index from documents...")
        return VectorStoreIndex.from_documents(
            documents=documents,
            storage_context=storage_context,
            embed_model=embedding_model,
        )

    def build_index_from_nodes(
        self, nodes: List[BaseNode], embedding_model, insert_batch_size: int = 16
    ):
        # Check service
        if self._vector_store == None:
            Logger.exception("Please set vector store")
            raise Exception("Please set vector store")

        # Check input
        assert isinstance(nodes, list), "Please insert list of nodes"
        assert nodes, "Data cannot be empty"

        # Build storage context
        storage_context = StorageContext.from_defaults(vector_store=self._vector_store)
        # Update state
        Logger.info("Building index from nodes...")

        return VectorStoreIndex(
            nodes = nodes,
            storage_context=storage_context,
            embed_model=embedding_model,
            insert_batch_size=insert_batch_size,
        )

    def load_index(self, embedding_model):
        # Check service
        if self._vector_store == None:
            Logger.exception("Please set vector store")
            raise Exception("Please set vector store")

        # Build storage context
        storage_context = StorageContext.from_defaults(vector_store=self._vector_store)
        Logger.info("Loading index ...")
        return VectorStoreIndex.from_vector_store(
            vector_store=self._vector_store,
            storage_context=storage_context,
            embed_model=embedding_model,
        )
