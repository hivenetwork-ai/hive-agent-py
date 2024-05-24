from semantic_text_splitter import TextSplitter
from typing import Union,List,Tuple
from enum import Enum
from tokenizers import Tokenizer
from llama_index.core import Document

class SplitterType(Enum):
    CHARACTER_MODE = 0,
    TIKTOKEN_MODE = 1,
    HUGGINGFACE_MODE = 2

class SemanticTextSplitter():
    # Reference (https://pypi.org/project/semantic-text-splitter/)
    def __init__(self,splitter_mode = SplitterType.CHARACTER_MODE):
        super().__init__()
        # Base mode
        self.splitter = TextSplitter()
        if splitter_mode == SplitterType.HUGGINGFACE_MODE:
            tokenizer = Tokenizer.from_pretrained("bert-base-uncased")
            self.splitter = TextSplitter.from_huggingface_tokenizer(tokenizer)
        elif splitter_mode == SplitterType.TIKTOKEN_MODE:
            self.splitter = TextSplitter.from_tiktoken_model("gpt-3.5-turbo")

    def from_text(self,input:Union[str,List[str]], max_characters : Union[int,Tuple[int]]= (100,1000)):
        if not type(input) == str:
            raise Exception("Please insert list of string")
        return self.splitter.chunks(input,max_characters)

    def from_documents(self,documents: List[Document],max_characters : Union[int,Tuple[int]]= (100,1000)):
        # Join document
        text = [doc.text for doc in documents]
        text = "\n".join(text)

        # Return value
        return self.splitter.chunks(text, max_characters)