from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from hive_agent.server.routes import files
import pickle 
import os

supported_exts = [".md", ".mdx", ".txt", ".csv", ".docx", ".pdf"]
index_base_dir= "hive-agent-data/index/store/"

os.makedirs(index_base_dir, exist_ok=True)

class IndexStore:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self.indexes = {}

    def save_to_file(self, file_path='indexes.pkl'):

        """Saves the current indexes to a file."""
        with open(index_base_dir+file_path, 'wb') as file:
            pickle.dump(self.indexes, file)
        return f"Indexes saved to {file_path}."

    @classmethod
    def load_from_file(cls, file_path='indexes.pkl'):
        """Loads indexes from a file."""
        with open(index_base_dir+file_path, 'rb') as file:
            loaded_indexes = pickle.load(file)
        instance = cls.get_instance()
        instance.indexes = loaded_indexes
        return instance
    
    def add_index(self, index_name, index):
        if index_name in self.indexes:
            raise ValueError("An index with this name already exists.")
        self.indexes[index_name] = index
        return f"Index '{index_name}' added successfully."

    def get_index(self, index_name):
        if index_name not in self.indexes:
            raise KeyError("No index found with this name.")
        return self.indexes[index_name]

    def update_index(self, index_name, new_index):
        if index_name not in self.indexes:
            raise KeyError("No index found with this name to update.")
        self.indexes[index_name] = new_index
        return f"Index '{index_name}' updated successfully."

    def delete_index(self, index_name):
        if index_name not in self.indexes:
            raise KeyError("No index found with this name to delete.")
        del self.indexes[index_name]
        return f"Index '{index_name}' deleted successfully."

    def list_indexes(self):
        return list(self.indexes.keys())

    def get_all_indexes(self):
        """Returns a list of all index objects stored in the index store."""
        return list(self.indexes.values())

class RetrieverBase:
    def __init__(
        self,
        required_exts=supported_exts,
        retrieve_data_path=files.BASE_DIR,
        name="BaseRetriever",
        description="This tool creates a base retriever index",
    ):
        self.retrieve_data_path = retrieve_data_path
        self.required_exts = required_exts
        self.name = name
        self.description = description

    def _load_documents(self, file_path=None, folder_path=None):
        if file_path is None:
            if folder_path is None:
                folder_path = self.retrieve_data_path

        reader = SimpleDirectoryReader(
            input_files=file_path,
            input_dir=folder_path,
            required_exts=self.required_exts,
            recursive=True,
            filename_as_id=True,
        )
        return reader.load_data()

    def create_basic_index(self, file_path=None, folder_path=None):
        documents = self._load_documents(file_path, folder_path)
        index = VectorStoreIndex.from_documents(documents)
        return index

    def insert_documents(self, index, file_path=None, folder_path=None):
        documents = self._load_documents(file_path, folder_path)
        if not documents:
            raise KeyError("No documents found to insert.")

        for document in documents:
            index.insert(document)

        return f"{len(documents)} documents inserted successfully."

    def update_documents(self, index, file_path=None, folder_path=None):
        documents = self._load_documents(file_path, folder_path)
        if not documents:
            raise KeyError("No documents found to update.")

        index.refresh(documents)
        return f"{len(documents)} documents updated successfully."

    def delete_documents(self, index, file_path=None, folder_path=None):
        documents = self._load_documents(file_path, folder_path)
        if not documents:
            raise KeyError("No documents found to delete.")

        document_ids = [doc.doc_id for doc in documents]
        for doc_id in document_ids:
            index.delete(doc_id)

        return f"{len(document_ids)} documents deleted successfully."



    