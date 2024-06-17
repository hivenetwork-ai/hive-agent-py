from datetime import datetime
from typing import List
from llama_index.agent.openai import OpenAIAgent
from llama_index.core.llms import ChatMessage, MessageRole

from hive_agent.database.database import DatabaseManager


class ChatManager:
    def __init__(self, llm, user_id: str, session_id: str):
        self.llm = llm
        self.user_id = user_id
        self.session_id = session_id
        self.chat_store_key = f"{user_id}_{session_id}"

    async def add_message(
        self, db_manager: DatabaseManager, role: str, content: str
    ):
        if not isinstance(content, str):
            content = content.response

        message = ChatMessage(role=role, content=content)
        await db_manager.insert_data(
            "chats",
            {
                "user_id": self.user_id,
                "session_id": self.session_id,
                "message": content,
                "role": role,
                "timestamp": datetime.utcnow().isoformat(),
            },
        )

    async def get_messages(self, db_manager: DatabaseManager):
        filters = {"user_id": [self.user_id], "session_id": [self.session_id]}
        db_chat_history = await db_manager.read_data("chats", filters)
        chat_history = [
            ChatMessage(role=chat["role"], content=chat["message"])
            for chat in db_chat_history
        ]
        return chat_history

    async def generate_response(
        self,
        db_manager: DatabaseManager,
        messages: List[ChatMessage],
        last_message: ChatMessage,
    ):
        chat_history = await self.get_messages(db_manager)
        await self.add_message(db_manager, last_message.role.value, last_message.content)

        if isinstance(self.llm, OpenAIAgent):
            response_stream = await self.llm.astream_chat(last_message.content, chat_history=chat_history)
            assistant_message = "".join([token async for token in response_stream.async_response_gen()])
        else:
            response = await self.llm.achat(last_message.content, chat_history=chat_history)
            assistant_message = response.response if hasattr(response, 'response') else str(response)

        await self.add_message(db_manager, MessageRole.ASSISTANT, assistant_message)

        return assistant_message
