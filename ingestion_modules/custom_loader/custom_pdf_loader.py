from llama_index.readers.file import pymu_pdf,unstructured
from llama_parse.base import LlamaParse
from config import params
from typing import Union,List,Literal
from pathlib import Path
from system_component.system_logging import Logger
import os
LLAMAPARSE_KEY = params.LLAMAPARSE_KEY

class CustomPDFReader():
    def __init__(self,pdf_provider : Literal["PyMuPDF","Unstructured","LlamaParse"] = "PyMuPDF"):
        # Define variable
        self._pdf_provider = pdf_provider

        self._reader = None
        # Get object
        # PyMuPDF Reader
        if self._pdf_provider == "PyMuPDF":
            self._reader = pymu_pdf.PyMuPDFReader()

        # UNSTRUCTURED Reader
        elif self._pdf_provider == "Unstructured":
            self._reader = unstructured.UnstructuredReader()
        # LlamaParse Reader
        elif self._pdf_provider == "LlamaParse":
            assert LLAMAPARSE_KEY, "LlamaParser key cant be empty"
            self._reader = LlamaParse(api_key=LLAMAPARSE_KEY)
        else:
            raise Exception(f"Service {self._pdf_provider} is not supported!")
        Logger.info(f"Document parser with {self._pdf_provider}")


    def load_data(self,file_path:Union[List[str],str]):

        # Check file existed
        if isinstance(file_path,str):
            if not os.path.exists(file_path):
                raise Exception("File is not existed!")
        Logger.info("Loading PDF document")
        # Return value
        return self._reader.load_data(file_path)

    async def aload_data(self,file_path:Union[List[str],str]):
        # Check file existed
        if isinstance(file_path, str):
            if not os.path.exists(file_path):
                raise Exception("File is not existed!")
        # Return value
        data = await self._reader.aload_data(file_path)
        return data

