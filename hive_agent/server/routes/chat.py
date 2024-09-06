import logging
import os
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Depends, Request, Query, status, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from hive_agent.database.database import get_db, DatabaseManager
from hive_agent.chat import ChatManager
from hive_agent.chat.schemas import ChatHistorySchema, ChatRequest, ChatData
from llama_index.core.llms import ChatMessage, MessageRole
from llama_index.agent.openai import OpenAIAgent  # type: ignore
from hive_agent.filestore import FileStore, BASE_DIR
from hive_agent.sdk_context import SDKContext
from langtrace_python_sdk import inject_additional_attributes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
file_store = FileStore(BASE_DIR)


def setup_chat_routes(router: APIRouter, id, sdk_context: SDKContext):
    async def validate_chat_data(chat_data):
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
        return last_message, [ChatMessage(role=m.role, content=m.content) for m in chat_data.messages]

    async def process_llm_response(
        request: Request, chat_manager: ChatManager, last_message_content: str, messages: List[ChatMessage]
    ):
        async def event_generator():
            async for token in response.async_response_gen():
                if await request.is_disconnected():
                    break
                yield token

        if isinstance(chat_manager.llm, OpenAIAgent):
            response = await chat_manager.llm.astream_chat(last_message_content, messages)
            return StreamingResponse(event_generator(), media_type="text/plain")
        return None

    async def generate_response_or_stream(
        chat_manager: ChatManager,
        db_manager: DatabaseManager,
        request: Request,
        last_chat_message: ChatMessage,
        messages: List[ChatMessage],
        file_paths: Optional[List[str]] = None,
    ):
        llm_response = await process_llm_response(request, chat_manager, str(last_chat_message.content), messages)
        if llm_response:
            return llm_response
        return await chat_manager.generate_response(db_manager, messages, last_chat_message, file_paths or [])

    @router.post("/chat")
    async def chat(
        request: Request,
        chat_request: ChatRequest,
        db: AsyncSession = Depends(get_db),
    ):
        attributes = sdk_context.get_attributes(id, 'llm', 'agent_class', 'tools', 'instruction', 'tool_retriever')
        llm_instance = attributes['agent_class'](attributes['llm'], attributes['tools'], attributes['instruction'], attributes['tool_retriever']).agent

        chat_manager = ChatManager(llm_instance, user_id=chat_request.user_id, session_id=chat_request.session_id)
        db_manager = DatabaseManager(db)

        last_message, messages = await validate_chat_data(chat_request.chat_data)

        file_paths = (
            [f"{BASE_DIR}/{media.value}" for media in chat_request.media_references if media.type.value == "file_name"]
            if chat_request.media_references
            else []
        )

        return await inject_additional_attributes(lambda: generate_response_or_stream(
            chat_manager,
            db_manager,
            request,
            ChatMessage(role=last_message.role, content=last_message.content),
            messages,
            file_paths,
        ), {
            # "agent_id": os.getenv("HIVE_AGENT_ID", ""),
            "user_id": chat_request.user_id,
            # "session_id": chat_request.session_id
        })

    @router.post("/chat_media")
    async def chat_media(
        request: Request,
        user_id: str = Form(...),
        session_id: str = Form(...),
        chat_data: str = Form(...),
        files: List[UploadFile] = File(...),
        db: AsyncSession = Depends(get_db),
    ):
        try:
            chat_data_parsed = ChatData.model_validate_json(chat_data)
        except ValidationError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Chat data is malformed: {e.json()}",
            )

        if len(files) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No files provided",
            )
        
        attributes = sdk_context.get_attributes(id, 'llm', 'agent_class', 'tools', 'instruction', 'tool_retriever')
        llm_instance = attributes['agent_class'](attributes['llm'], attributes['tools'], attributes['instruction'], attributes['tool_retriever']).agent

        chat_manager = ChatManager(llm_instance, user_id=user_id, session_id=session_id)
        db_manager = DatabaseManager(db)

        last_message, messages = await validate_chat_data(chat_data_parsed)

        file_paths = [f"{BASE_DIR}/{await file_store.save_file(file)}" for file in files]

        return await inject_additional_attributes(lambda: generate_response_or_stream(
            chat_manager,
            db_manager,
            request,
            ChatMessage(role=last_message.role, content=last_message.content),
            messages,
            file_paths,
        ), {
            # "agent_id": os.getenv("HIVE_AGENT_ID", ""),
            "user_id": user_id,
            # "session_id": session_id
        })

    @router.get("/chat_history", response_model=List[ChatHistorySchema])
    async def get_chat_history(
        user_id: str = Query(...),
        session_id: str = Query(...),
        db: AsyncSession = Depends(get_db),
    ):
        
        attributes = sdk_context.get_attributes(id, 'llm', 'agent_class', 'tools', 'instruction', 'tool_retriever')
        llm_instance = attributes['agent_class'](attributes['llm'], attributes['tools'], attributes['instruction'], attributes['tool_retriever']).agent

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
                timestamp=str(datetime.now(timezone.utc)),
            )
            for msg in chat_history
        ]

    @router.get("/all_chats")
    async def get_all_chats(user_id: str = Query(...), db: AsyncSession = Depends(get_db)):

        attributes = sdk_context.get_attributes(id, 'llm', 'agent_class', 'tools', 'instruction', 'tool_retriever')
        llm_instance = attributes['agent_class'](attributes['llm'], attributes['tools'], attributes['instruction'], attributes['tool_retriever']).agent

        chat_manager = ChatManager(llm_instance, user_id=user_id, session_id="")
        db_manager = DatabaseManager(db)
        all_chats = await chat_manager.get_all_chats_for_user(db_manager)

        if not all_chats:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No chats found for this user",
            )

        return all_chats
