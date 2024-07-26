import pytest
from unittest.mock import MagicMock, patch
from hive_agent.tools.retriever.base_retrieve import RetrieverBase, IndexStore


@pytest.fixture
def retriever_base():
    return RetrieverBase()


@pytest.fixture
def index_store():
    IndexStore._instance = None  # Reset singleton instance before each test
    return IndexStore.get_instance()


def test_retriever_base_initialization(retriever_base):
    assert retriever_base.name == "BaseRetriever"
    assert retriever_base.description == "This tool creates a base retriever index"
    assert retriever_base.required_exts == [".md", ".mdx", ".txt", ".csv", ".docx", ".pdf"]
    assert retriever_base.retrieve_data_path == "hive-agent-data/files/user"

@patch('llama_index.core.SimpleDirectoryReader.load_data')
@patch('llama_index.core.VectorStoreIndex.from_documents', return_value="index")
def test_create_basic_index(mock_from_documents, mock_load_data, retriever_base):
    # Added line
    mock_load_data.return_value = [MagicMock(doc_id="doc1"), MagicMock(doc_id="doc2")]
    index = retriever_base.create_basic_index()
    mock_load_data.assert_called_once()
    mock_from_documents.assert_called_once_with(mock_load_data.return_value)
    assert index == "index"


@patch('llama_index.core.SimpleDirectoryReader.load_data')
def test_insert_documents(mock_load_data, retriever_base):
    # Added line
    mock_load_data.return_value = [MagicMock(doc_id="doc1"), MagicMock(doc_id="doc2")]
    mock_index = MagicMock()
    result = retriever_base.insert_documents(mock_index)
    mock_load_data.assert_called_once()
    assert mock_index.insert.call_count == 2
    assert result == "2 documents inserted successfully."


@patch('llama_index.core.SimpleDirectoryReader.load_data')
def test_update_documents(mock_load_data, retriever_base):
    # Added line
    mock_load_data.return_value = [MagicMock(doc_id="doc1"), MagicMock(doc_id="doc2")]
    mock_index = MagicMock()
    result = retriever_base.update_documents(mock_index)
    mock_load_data.assert_called_once()
    mock_index.refresh.assert_called_once_with(mock_load_data.return_value)
    assert result == "2 documents updated successfully."


@patch('llama_index.core.SimpleDirectoryReader.load_data')
def test_delete_documents(mock_load_data, retriever_base):
    # Added line
    mock_load_data.return_value = [MagicMock(doc_id="doc1"), MagicMock(doc_id="doc2")]
    mock_index = MagicMock()
    result = retriever_base.delete_documents(mock_index)
    mock_load_data.assert_called_once()
    mock_index.delete.assert_any_call("doc1")
    mock_index.delete.assert_any_call("doc2")
    assert result == "2 documents deleted successfully."


def test_index_store_singleton():
    store1 = IndexStore.get_instance()
    store2 = IndexStore.get_instance()
    assert store1 is store2


def test_add_index(index_store):
    mock_index = MagicMock()
    result = index_store.add_index("test_index", mock_index)
    assert result == "Index 'test_index' added successfully."
    assert index_store.get_index("test_index") == mock_index


def test_add_index_existing_name(index_store):
    mock_index = MagicMock()
    index_store.add_index("test_index", mock_index)
    with pytest.raises(ValueError, match="An index with this name already exists."):
        index_store.add_index("test_index", mock_index)


def test_get_index(index_store):
    mock_index = MagicMock()
    index_store.add_index("test_index", mock_index)
    assert index_store.get_index("test_index") == mock_index


def test_get_index_nonexistent(index_store):
    with pytest.raises(KeyError, match="No index found with this name."):
        index_store.get_index("nonexistent_index")


def test_update_index(index_store):
    mock_index = MagicMock()
    index_store.add_index("test_index", mock_index)
    new_mock_index = MagicMock()
    result = index_store.update_index("test_index", new_mock_index)
    assert result == "Index 'test_index' updated successfully."
    assert index_store.get_index("test_index") == new_mock_index


def test_update_index_nonexistent(index_store):
    mock_index = MagicMock()
    with pytest.raises(KeyError, match="No index found with this name to update."):
        index_store.update_index("nonexistent_index", mock_index)


def test_delete_index(index_store):
    mock_index = MagicMock()
    index_store.add_index("test_index", mock_index)
    result = index_store.delete_index("test_index")
    assert result == "Index 'test_index' deleted successfully."
    with pytest.raises(KeyError, match="No index found with this name."):
        index_store.get_index("test_index")


def test_delete_index_nonexistent(index_store):
    with pytest.raises(KeyError, match="No index found with this name to delete."):
        index_store.delete_index("nonexistent_index")


def test_list_indexes(index_store):
    mock_index1 = MagicMock()
    mock_index2 = MagicMock()
    index_store.add_index("index1", mock_index1)
    index_store.add_index("index2", mock_index2)
    assert index_store.list_indexes() == ["index1", "index2"]


def test_get_all_indexes(index_store):
    mock_index1 = MagicMock()
    mock_index2 = MagicMock()
    index_store.add_index("index1", mock_index1)
    index_store.add_index("index2", mock_index2)
    assert index_store.get_all_indexes() == [mock_index1, mock_index2]