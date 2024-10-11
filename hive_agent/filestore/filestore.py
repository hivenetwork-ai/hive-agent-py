import logging
import os
import shutil

import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from dotenv import load_dotenv
from fastapi import UploadFile

load_dotenv()

BASE_DIR = "hive-agent-data/files/user"
USE_S3 = os.getenv("USE_S3", "false").lower() == "true"
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
AWS_REGION = os.getenv("AWS_DEFAULT_REGION")

# TODO: get log level from config
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FileStore:
    def __init__(self, base_dir: str):
        self.use_s3 = USE_S3
        self.base_dir = base_dir

        if self.use_s3:
            if not S3_BUCKET_NAME:
                logger.error("S3_BUCKET_NAME environment variable is not set.")
                raise ValueError("S3_BUCKET_NAME environment variable is required when USE_S3 is true.")
            self.s3_client = boto3.client("s3", region_name=AWS_REGION)
            logger.info(f"Initialized FileStore with S3 bucket: {S3_BUCKET_NAME}")
        else:
            os.makedirs(self.base_dir, exist_ok=True)
            logger.info(f"Initialized FileStore with base directory: {self.base_dir}")

    async def save_file(self, file: UploadFile):
        filename = os.path.basename(str(file.filename))
        if not filename:
            logger.error("Attempted to save a file with an empty name.")
            raise ValueError("Filename cannot be empty.")

        if self.use_s3:
            try:
                self.s3_client.upload_fileobj(file.file, S3_BUCKET_NAME, filename)
                logger.info(f"Uploaded file: {filename} to S3 bucket: {S3_BUCKET_NAME}")
            except NoCredentialsError:
                logger.error("AWS credentials not available.")
                raise
            except ClientError as e:
                logger.error(f"Failed to upload file to S3: {e}")
                raise IOError(f"Error uploading file {filename} to S3")
        else:
            file_location = os.path.join(self.base_dir, filename)
            try:
                with open(file_location, "wb") as buffer:
                    shutil.copyfileobj(file.file, buffer)
                logger.info(f"Saved file: {filename} at {file_location}")
            except Exception as e:
                logger.error(f"Failed to save file {filename}: {e}")
                raise IOError(f"Error saving file {filename}")

        return filename

    def delete_file(self, filename: str):
        if not filename:
            logger.error("Attempted to delete a file with an empty name.")
            raise ValueError("Filename cannot be empty.")

        if self.use_s3:
            try:
                self.s3_client.delete_object(Bucket=S3_BUCKET_NAME, Key=filename)
                logger.info(f"Deleted file: {filename} from S3 bucket: {S3_BUCKET_NAME}")
                return True
            except ClientError as e:
                logger.error(f"Failed to delete file from S3: {e}")
                raise IOError(f"Error deleting file {filename} from S3")
        else:
            file_location = os.path.join(self.base_dir, filename)
            if os.path.exists(file_location):
                try:
                    os.remove(file_location)
                    logger.info(f"Deleted file: {filename}")
                    return True
                except Exception as e:
                    logger.error(f"Failed to delete file {filename}: {e}")
                    raise IOError(f"Error deleting file {filename}")
            else:
                logger.warning(f"Attempted to delete non-existent file: {filename}")
                return False

    def list_files(self):
        if self.use_s3:
            try:
                response = self.s3_client.list_objects_v2(Bucket=S3_BUCKET_NAME)
                if "Contents" in response:
                    files = [obj["Key"] for obj in response["Contents"]]
                else:
                    files = []
                logger.info(f"Listed files from S3 bucket: {files}")
                return files
            except ClientError as e:
                logger.error(f"Failed to list files from S3: {e}")
                raise IOError("Error listing files from S3")
        else:
            try:
                files = os.listdir(self.base_dir)
                logger.info(f"Listed files: {files}")
                return files
            except Exception as e:
                logger.error(f"Failed to list files: {e}")
                raise IOError("Error listing files")

    def rename_file(self, old_filename: str, new_filename: str):
        if not old_filename or not new_filename:
            logger.error("Attempted to rename with an empty name.")
            raise ValueError("Filenames cannot be empty.")

        if self.use_s3:
            copy_source = {"Bucket": S3_BUCKET_NAME, "Key": old_filename}
            try:
                # Copy the object to the new key
                self.s3_client.copy(copy_source, S3_BUCKET_NAME, new_filename)
                # Delete the old object
                self.s3_client.delete_object(Bucket=S3_BUCKET_NAME, Key=old_filename)
                logger.info(f"Renamed file from {old_filename} to {new_filename} in S3 bucket: {S3_BUCKET_NAME}")
                return True
            except ClientError as e:
                logger.error(f"Failed to rename file in S3: {e}")
                raise IOError(f"Error renaming file {old_filename} to {new_filename} in S3")
        else:
            old_file_location = os.path.join(self.base_dir, old_filename)
            new_file_location = os.path.join(self.base_dir, new_filename)

            if os.path.exists(old_file_location):
                try:
                    os.rename(old_file_location, new_file_location)
                    logger.info(f"Renamed file from {old_filename} to {new_filename}")
                    return True
                except Exception as e:
                    logger.error(f"Failed to rename file from {old_filename} to {new_filename}: {e}")
                    raise IOError(f"Error renaming file {old_filename}")
            else:
                logger.warning(f"Attempted to rename non-existent file: {old_filename}")
                return False
