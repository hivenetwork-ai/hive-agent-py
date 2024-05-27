from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
import logging
from hive_agent.filestore import FileStore


# TODO: get log level from config
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


BASE_DIR = "hive-agent-data/files/user"
ALLOWED_FILE_TYPES = ['application/json', 'text/csv', 'text/plain', 'application/pdf']

file_store = FileStore(BASE_DIR)


def setup_files_routes(router: APIRouter):
    @router.post("/uploadfiles/")
    async def create_upload_files(files: List[UploadFile] = File(...)):
        saved_files = []
        for file in files:
            if not file.content_type:
                logger.warning(f"File {file.filename} has no content type.")
                raise HTTPException(status_code=400, detail="File content type is missing.")

            if file.content_type not in ALLOWED_FILE_TYPES:
                logger.warning(f"Disallowed file type upload attempted: {file.content_type}")
                raise HTTPException(status_code=400, detail=f"File type {file.content_type} is not allowed.")

            try:
                filename = await file_store.save_file(file)
                saved_files.append(filename)
            except ValueError as e:
                logger.error(f"Value error: {e}")
                raise HTTPException(status_code=400, detail=str(e))
            except IOError as e:
                logger.error(f"I/O error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
            finally:
                await file.close()
                logger.info(f"Closed file {file.filename}")

        logger.info(f"Uploaded files: {saved_files}")
        return {"filenames": saved_files}

    @router.get("/files/")
    async def list_files():
        try:
            files = file_store.list_files()
            logger.info("Listed files")
            return {"files": files}
        except IOError as e:
            logger.error(f"I/O error: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @router.delete("/files/{filename}")
    async def delete_file(filename: str):
        try:
            if file_store.delete_file(filename):
                logger.info(f"Deleted file {filename}")
                return {"message": f"File {filename} deleted successfully."}
            else:
                logger.warning(f"File {filename} not found for deletion")
                raise HTTPException(status_code=404, detail=f"File {filename} not found.")
        except ValueError as e:
            logger.error(f"Value error: {e}")
            raise HTTPException(status_code=400, detail=str(e))
        except IOError as e:
            logger.error(f"I/O error: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @router.put("/files/{old_filename}/{new_filename}")
    async def rename_file(old_filename: str, new_filename: str):
        try:
            if file_store.rename_file(old_filename, new_filename):
                logger.info(f"Renamed file from {old_filename} to {new_filename}")
                return {"message": f"File {old_filename} renamed to {new_filename} successfully."}
            else:
                logger.warning(f"File {old_filename} not found for renaming")
                raise HTTPException(status_code=404, detail=f"File {old_filename} not found.")
        except ValueError as e:
            logger.error(f"Value error: {e}")
            raise HTTPException(status_code=400, detail=str(e))
        except IOError as e:
            logger.error(f"I/O error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
