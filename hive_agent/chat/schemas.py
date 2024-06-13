from typing import List
from pydantic import BaseModel
from llama_index.core.llms import MessageRole


class Message(BaseModel):
    role: MessageRole
    content: str


class ChatData(BaseModel):
    messages: List[Message]


class ChatHistorySchema(BaseModel):
    user_id: str
    session_id: str
    message: str
    role: str
    timestamp: str


class ChatRequest(BaseModel):
    user_id: str
    session_id: str
    chat_data: ChatData
