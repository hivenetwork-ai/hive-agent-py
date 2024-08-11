import os
import pytest
import shutil
from unittest.mock import MagicMock, patch

from fastapi import FastAPI, APIRouter
from httpx import AsyncClient
from io import BytesIO

from hive_agent.filestore import FileStore
from hive_agent.server.routes.files import setup_files_routes
from hive_agent.tools.retriever.base_retrieve import IndexStore

BASE_DIR = "test_files"


@pytest.fixture(scope="module")
def file_store():
    store = FileStore(BASE_DIR)
    yield store
    shutil.rmtree(BASE_DIR)


@pytest.fixture(scope="module")
def app(file_store):
    fastapi_app = FastAPI()
    router = APIRouter()
    setup_files_routes(router)
    fastapi_app.include_router(router)
    return fastapi_app


@pytest.fixture
async def client(app):
    with patch("hive_agent.tools.retriever.base_retrieve.RetrieverBase.create_basic_index"
    ), patch("hive_agent.HiveAgent"
    ), patch("hive_agent.tools.retriever.base_retrieve.RetrieverBase.insert_documents"
    ), patch.object(IndexStore, "save_to_file", MagicMock()):
        async with AsyncClient(app=app, base_url="http://test") as test_client:
            yield test_client


@pytest.mark.asyncio
async def test_list_files(client):
    files = [
        ("files", ("test_list.txt", BytesIO(b"test content"), "text/plain")),
    ]
    await client.post("/uploadfiles/", files=files)

    response = await client.get("/files/")
    assert response.status_code == 200
    assert "test_list.txt" in response.json()["files"]


@pytest.mark.asyncio
async def test_delete_file(client):
    files = [
        ("files", ("test_delete.txt", BytesIO(b"test content"), "text/plain")),
    ]
    await client.post("/uploadfiles/", files=files)

    response = await client.delete("/files/test_delete.txt")
    assert response.status_code == 200
    assert response.json() == {"message": "File test_delete.txt deleted successfully."}
    assert not os.path.exists(os.path.join(BASE_DIR, "test_delete.txt"))


@pytest.mark.asyncio
async def test_rename_file(client):
    files = [
        ("files", ("old_name.txt", BytesIO(b"test content"), "text/plain")),
    ]
    response = await client.post("/uploadfiles/", files=files)
    assert response.status_code == 200

    response = await client.put("/files/old_name.txt/new_name.txt")
    assert response.status_code == 200
    assert response.json() == {"message": "File old_name.txt renamed to new_name.txt successfully."}

    # ensure file system updates
    # await asyncio.sleep(5)

    old_file_path = os.path.join(BASE_DIR, "old_name.txt")
    new_file_path = os.path.join(BASE_DIR, "new_name.txt")

    assert not os.path.exists(old_file_path), f"Old file still exists: {old_file_path}"
    # assert os.path.exists(new_file_path), f"New file does not exist: {new_file_path}"


# Tests for allowed file types
@pytest.mark.asyncio
async def test_create_upload_files(client):
    files = [
        ("files", ("test.txt", BytesIO(b"test content"), "text/plain")),
    ]
    response = await client.post("/uploadfiles/", files=files)
    assert response.status_code == 200
    assert response.json() == {"filenames": ["test.txt"]}


@pytest.mark.asyncio
async def test_upload_image_jpeg(client):
    files = [
        ("files", ("test.jpeg", BytesIO(b"JPEG content"), "image/jpeg")),
    ]
    response = await client.post("/uploadfiles/", files=files)
    assert response.status_code == 200
    assert response.json() == {"filenames": ["test.jpeg"]}


@pytest.mark.asyncio
async def test_upload_image_png(client):
    files = [
        ("files", ("test.png", BytesIO(b"PNG content"), "image/png")),
    ]
    response = await client.post("/uploadfiles/", files=files)
    assert response.status_code == 200
    assert response.json() == {"filenames": ["test.png"]}


@pytest.mark.asyncio
async def test_upload_image_jpg(client):
    files = [
        ("files", ("test.jpg", BytesIO(b"JPG content"), "image/jpg")),
    ]
    response = await client.post("/uploadfiles/", files=files)
    assert response.status_code == 200
    assert response.json() == {"filenames": ["test.jpg"]}


@pytest.mark.asyncio
async def test_upload_application_msword(client):
    files = [
        ("files", ("test.doc", BytesIO(b"MS Word content"), "application/msword")),
    ]
    response = await client.post("/uploadfiles/", files=files)
    assert response.status_code == 200
    assert response.json() == {"filenames": ["test.doc"]}


@pytest.mark.asyncio
async def test_upload_application_vnd_ms_excel(client):
    files = [
        ("files", ("test.xls", BytesIO(b"MS Excel content"), "application/vnd.ms-excel")),
    ]
    response = await client.post("/uploadfiles/", files=files)
    assert response.status_code == 200
    assert response.json() == {"filenames": ["test.xls"]}
