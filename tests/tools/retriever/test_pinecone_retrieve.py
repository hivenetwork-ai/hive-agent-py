import unittest
from unittest.mock import MagicMock, patch, ANY
import os
from hive_agent.tools.retriever.pinecone_retrieve import PineconeRetriever
class TestPineconeRetriever(unittest.TestCase):

    @patch.dict(os.environ, {'PINECONE_API_KEY': 'fake_api_key'})
    def setUp(self):
        self.pinecone_client_mock = MagicMock()
        self.pinecone_client_mock.create_index = MagicMock()  
        self.pinecone_client_mock.Index = MagicMock() 
        self.retriever = PineconeRetriever()
        self.retriever.pinecone_client = self.pinecone_client_mock

    @patch('hive_agent.tools.retriever.pinecone_retrieve.PineconeVectorStore')
    @patch('hive_agent.tools.retriever.pinecone_retrieve.StorageContext')
    @patch('hive_agent.tools.retriever.pinecone_retrieve.VectorStoreIndex')
    def test_create_index(self, VectorStoreIndexMock, StorageContextMock, PineconeVectorStoreMock):
        self.retriever._load_documents = MagicMock(return_value=(['doc1', 'doc2'], ['file1.txt', 'file2.txt']))

        index, file_names = self.retriever.create_serverless_index(file_path='dummy_path')

        self.pinecone_client_mock.create_index.assert_called_once_with(
            name="hive-agent-pinecone",
            dimension=1536,
            metric="euclidean",
            spec=ANY 
        )
        self.pinecone_client_mock.Index.assert_called_once_with("hive-agent-pinecone")
        PineconeVectorStoreMock.assert_called_once()
        StorageContextMock.from_defaults.assert_called_once()
        VectorStoreIndexMock.from_documents.assert_called_once_with(
            ['doc1', 'doc2'], storage_context=StorageContextMock.from_defaults.return_value
        )
        self.assertEqual(index, VectorStoreIndexMock.from_documents.return_value)
        self.assertEqual(file_names, ['file1.txt', 'file2.txt'])

    @patch('hive_agent.tools.retriever.pinecone_retrieve.PineconeVectorStore')
    @patch('hive_agent.tools.retriever.pinecone_retrieve.StorageContext')
    @patch('hive_agent.tools.retriever.pinecone_retrieve.VectorStoreIndex')
    def test_create_pod_index(self, VectorStoreIndexMock, StorageContextMock, PineconeVectorStoreMock):
        self.retriever._load_documents = MagicMock(return_value=(['doc1', 'doc2'], ['file1.txt', 'file2.txt']))

        index, file_names = self.retriever.create_pod_index(file_path='dummy_path')

        self.pinecone_client_mock.create_index.assert_called_once_with(
            name="hive-agent-pinecone-pod",
            dimension=1536,
            metric="cosine",
            spec=ANY
        )
        self.pinecone_client_mock.Index.assert_called_once_with("hive-agent-pinecone-pod")
        PineconeVectorStoreMock.assert_called_once()
        StorageContextMock.from_defaults.assert_called_once()
        VectorStoreIndexMock.from_documents.assert_called_once_with(
            ['doc1', 'doc2'], storage_context=StorageContextMock.from_defaults.return_value
        )
        self.assertEqual(index, VectorStoreIndexMock.from_documents.return_value)
        self.assertEqual(file_names, ['file1.txt', 'file2.txt'])