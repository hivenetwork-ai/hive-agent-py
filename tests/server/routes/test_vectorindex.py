import pytest
from httpx import AsyncClient
from fastapi import FastAPI, APIRouter
from hive_agent.server.routes.vectorindex import setup_vectorindex_routes
from unittest.mock import MagicMock, patch
import os 

@pytest.fixture(scope="module")
def app():
    fastapi_app = FastAPI()
    router = APIRouter()
    setup_vectorindex_routes(router)
    fastapi_app.include_router(router)
    return fastapi_app

@pytest.fixture
async def client(app):
    async with AsyncClient(app=app, base_url="http://test") as test_client:
        yield test_client


@pytest.mark.asyncio
async def test_create_index_basic(client):
    with patch('hive_agent.tools.retriever.base_retrieve.RetrieverBase.create_basic_index'):
        params = {
            "index_name": "test_basic",
            "index_type": "basic"
        }

        file_path = ["test.txt"]
        if file_path:
            for path in file_path:
                params["file_path"] = path

        folder_path = None
        if folder_path:
            params["folder_path"] = folder_path

        response = await client.post(
            "/create_index/",
            params=params
        )

        assert response.status_code == 200
        assert response.json()["message"] == "Index test_basic created successfully."

@pytest.mark.asyncio    
async def test_create_index_chroma(client):
    with patch('hive_agent.tools.retriever.chroma_retrieve.ChromaRetriever.create_index'):
    
        params = {
            "index_name": "test_chroma",
            "index_type": "chroma"
        }

        file_path = ["test.txt"]
        if file_path:
            for path in file_path:
                params["file_path"] = path

        folder_path = None
        if folder_path:
            params["folder_path"] = folder_path

        response = await client.post(
            "/create_index/",
            params=params
        )
        
        assert response.status_code == 200
        assert response.json()["message"] == "Index test_chroma created successfully."
        
@pytest.mark.asyncio 
async def test_create_index_pinecone_serverless(client):
    with patch('hive_agent.tools.retriever.pinecone_retrieve.PineconeRetriever.create_serverless_index'
        ),patch.dict(os.environ, {'PINECONE_API_KEY': 'fake_api_key'}):
    
        params = {
            "index_name": "test_pinecone_serverless",
            "index_type": "pinecone-serverless"
        }

        file_path = ["test.txt"]
        if file_path:
            for path in file_path:
                params["file_path"] = path

        folder_path = None
        if folder_path:
            params["folder_path"] = folder_path

        response = await client.post(
            "/create_index/",
            params=params
        )
        
        print(response.status_code)
        print(response.json())

        assert response.status_code == 200
        assert response.json()["message"] == "Index test_pinecone_serverless created successfully."

@pytest.mark.asyncio 
async def test_create_index_pinecone_pod(client):
    with patch('hive_agent.tools.retriever.pinecone_retrieve.PineconeRetriever.create_pod_index'
        ),patch.dict(os.environ, {'PINECONE_API_KEY': 'fake_api_key'}):
    
        params = {
            "index_name": "test_pinecone_pod",
            "index_type": "pinecone-pod"
        }

        file_path = ["test.txt"]
        if file_path:
            for path in file_path:
                params["file_path"] = path

        folder_path = None
        if folder_path:
            params["folder_path"] = folder_path

        response = await client.post(
            "/create_index/",
            params=params
        )
        
        print(response.status_code)
        print(response.json())

        assert response.status_code == 200
        assert response.json()["message"] == "Index test_pinecone_pod created successfully."


@pytest.mark.asyncio 
async def test_insert_documents(client):
   with patch('hive_agent.tools.retriever.base_retrieve.RetrieverBase.create_basic_index'):
        params = {
            "index_name": "test_insert",
            "index_type": "basic"
        }

        file_path = ["test.txt"]
        if file_path:
            for path in file_path:
                params["file_path"] = path

        folder_path = None
        if folder_path:
            params["folder_path"] = folder_path

        response = await client.post(
            "/create_index/",
            params=params
        )

        insert_params = {
            "index_name": "test_insert",
            "file_path" : ["test.txt"]
        }

        response = await client.post(
            "/insert_documents/",
            params=insert_params
        )
        
        assert response.status_code == 200
        assert response.json()["message"] == "Documents inserted successfully."


@pytest.mark.asyncio 
async def test_update_documents(client):
   with patch('hive_agent.tools.retriever.base_retrieve.RetrieverBase.create_basic_index'):
        params = {
            "index_name": "test_insert",
            "index_type": "basic"
        }

        file_path = ["test.txt"]
        if file_path:
            for path in file_path:
                params["file_path"] = path

        folder_path = None
        if folder_path:
            params["folder_path"] = folder_path

        response = await client.post(
            "/create_index/",
            params=params
        )

        insert_params = {
            "index_name": "test_insert",
            "file_path" : ["test.txt"]
        }

        response = await client.put(
            "/update_documents/",
            params=insert_params
        )
        
        assert response.status_code == 200
        assert response.json()["message"] == "Documents updated successfully."

@pytest.mark.asyncio 
async def test_delete_documents(client):
   with patch('hive_agent.tools.retriever.base_retrieve.RetrieverBase.create_basic_index'):
        params = {
            "index_name": "test_insert",
            "index_type": "basic"
        }

        file_path = ["test.txt"]
        if file_path:
            for path in file_path:
                params["file_path"] = path

        folder_path = None
        if folder_path:
            params["folder_path"] = folder_path

        response = await client.post(
            "/create_index/",
            params=params
        )

        insert_params = {
            "index_name": "test_insert",
            "file_path" : ["test.txt"]
        }

        response = await client.delete(
            "/delete_documents/",
            params=insert_params
        )
        
        assert response.status_code == 200
        assert response.json()["message"] == "Documents deleted successfully."

@pytest.mark.asyncio
async def test_create_index_basic(client):
    with patch('hive_agent.tools.retriever.base_retrieve.RetrieverBase.create_basic_index'):
        params = {
            "index_name": "test_invalid",
            "index_type": "invalid_type"
        }

        file_path = ["test.txt"]
        if file_path:
            for path in file_path:
                params["file_path"] = path

        folder_path = None
        if folder_path:
            params["folder_path"] = folder_path

        response = await client.post(
            "/create_index/",
            params=params
        )
        print(response.status_code)
        print(response.json())
        assert response.status_code == 400
        assert response.json()["detail"] == "Invalid index type provided."
