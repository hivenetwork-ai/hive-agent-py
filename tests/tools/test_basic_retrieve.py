import pytest
from unittest.mock import MagicMock,patch

from hive_agent.server.routes import files
from hive_agent.tools.agent_db.basic_retrieve import basic_retrieve

@pytest.fixture
def setup_test_directory(tmp_path):
    test_dir = tmp_path / "test_dir"
    test_dir.mkdir()
    
    file1 = test_dir / "doc1.txt"
    file1.write_text("This is a test document 1.")
    
    file2 = test_dir / "doc2.md"
    file2.write_text("This is a test document 2.")
    
    file3 = test_dir / "doc3.pdf"
    file3.write_text("This is a test document 3.")  
    
    return test_dir

def test_basic_retrieve(setup_test_directory, monkeypatch):
    mock_retriever = MagicMock()
    mock_retriever.retrieve.return_value = ['result1', 'result2']

    with patch(
        "llama_index.core.VectorStoreIndex.from_documents", return_value=MagicMock()
    ), patch(
        "llama_index.core.objects.ObjectIndex.from_objects", return_value=MagicMock(as_retriever=MagicMock(return_value=mock_retriever))
    ):    
        sample_tools = ['sample_tool_1', 'sample_tool_2', 'sample_tool_3']
        required_extensions = ['.txt', '.md']

        monkeypatch.setattr(files, "BASE_DIR", str(setup_test_directory))
        
        retriever = basic_retrieve(sample_tools, required_extensions)

        results = retriever.retrieve("sample_tool_1")

        assert retriever is not None, "The function should return a retriever object."
        assert hasattr(retriever, 'retrieve'), "The returned object should have a 'retrieve' method."
        assert len(results) > 0, "The retriever should return some results."