import logging
from datetime import datetime
from typing import List

from fastapi import APIRouter, HTTPException, Depends, Request, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from hive_agent.database.database import get_db, DatabaseManager
from hive_agent.chat import ChatManager
from hive_agent.chat.schemas import ChatHistorySchema, ChatRequest
from llama_index.core.llms import ChatMessage, MessageRole
from llama_index.agent.openai import OpenAIAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def setup_chat_routes(router: APIRouter, llm_instance):
    @router.post("/chat")
    async def chat(
        request: Request,
        chat_request: ChatRequest,
        db: AsyncSession = Depends(get_db),
    ):
        user_id = chat_request.user_id
        session_id = chat_request.session_id
        chat_data = chat_request.chat_data

        chat_manager = ChatManager(llm_instance, user_id=user_id, session_id=session_id)
        db_manager = DatabaseManager(db)

        if len(chat_data.messages) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No messages provided",
            )

        last_message = chat_data.messages.pop()
        if last_message.role != MessageRole.USER:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Last message must be from user",
            )

        last_chat_message = ChatMessage(
            role=last_message.role, content=last_message.content
        )
        messages = [
            ChatMessage(role=m.role, content=m.content) for m in chat_data.messages
        ]

        async def event_generator():
            async for token in response.async_response_gen():
                if await request.is_disconnected():
                    break
                yield token

        if isinstance(chat_manager.llm, OpenAIAgent):
            response = await chat_manager.llm.astream_chat(last_message.content, messages)
            return StreamingResponse(event_generator(), media_type="text/plain")
        else:
            response = await chat_manager.generate_response(
                db_manager, messages, last_chat_message
            )
            return response

    @router.get("/chat_history", response_model=List[ChatHistorySchema])
    async def get_chat_history(
        user_id: str = Query(...),
        session_id: str = Query(...),
        db: AsyncSession = Depends(get_db),
    ):
        chat_manager = ChatManager(llm_instance, user_id=user_id, session_id=session_id)
        db_manager = DatabaseManager(db)
        chat_history = await chat_manager.get_messages(db_manager)
        if not chat_history:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No chat history found for this user",
            )

        return [
            ChatHistorySchema(
                user_id=user_id,
                session_id=session_id,
                message=msg.content,
                role=msg.role,
                timestamp=str(datetime.utcnow()),
            )
            for msg in chat_history
        ]

    @router.get("/all_chats")
    async def get_all_chats(
        user_id: str = Query(...), db: AsyncSession = Depends(get_db)
    ):
        chat_manager = ChatManager(llm_instance, user_id=user_id, session_id="")
        db_manager = DatabaseManager(db)
        all_chats = await chat_manager.get_all_chats_for_user(db_manager)

        if not all_chats:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No chats found for this user",
            )

        return all_chats
