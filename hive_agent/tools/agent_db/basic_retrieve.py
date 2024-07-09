from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.core.objects import ObjectIndex

from dotenv import load_dotenv

load_dotenv()


def basic_retrieve(tools: list, required_exts: list):

    retreive_data_path = "./hive-agent-data/files/user/"

    reader = SimpleDirectoryReader(
        input_dir=retreive_data_path,
        required_exts=required_exts,
        recursive=True,
    )
    documents = reader.load_data()

    index = VectorStoreIndex.from_documents(documents)
    vectorstore_object = ObjectIndex.from_objects(
        tools,
        index=index,
    )
    tool_retriever = vectorstore_object.as_retriever(similarity_top_k=3)

    return tool_retriever
