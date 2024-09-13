import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import List

from fastapi import APIRouter, Depends, Form, HTTPException, Query, Request, UploadFile, status
from fastapi.responses import StreamingResponse
from hive_agent.chat import ChatManager
from hive_agent.chat.schemas import ChatData, ChatHistorySchema
from hive_agent.database.database import DatabaseManager, get_db
from hive_agent.filestore import BASE_DIR, FileStore
from hive_agent.sdk_context import SDKContext
from langtrace_python_sdk import inject_additional_attributes  # type: ignore   # noqa
from llama_index.agent.openai import OpenAIAgent  # type: ignore
from llama_index.core.llms import ChatMessage, MessageRole
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
file_store = FileStore(BASE_DIR)


ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff"}


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

        # if isinstance(chat_manager.llm, OpenAIAgent):
        response = await chat_manager.llm.astream_chat(last_message_content, messages)
        return StreamingResponse(event_generator(), media_type="text/plain")
        # return None

    @router.post("/chat")
    async def chat(
        request: Request,
        user_id: str = Form(...),
        session_id: str = Form(...),
        chat_data: str = Form(...),
        files: List[UploadFile] = [],
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

        attributes = sdk_context.get_attributes(id, "llm", "agent_class", "tools", "instruction", "tool_retriever")
        llm_instance = attributes["agent_class"](
            attributes["llm"], attributes["tools"], attributes["instruction"], attributes["tool_retriever"]
        ).agent

        chat_manager = ChatManager(llm_instance, user_id=user_id, session_id=session_id)
        db_manager = DatabaseManager(db)

        last_message, messages = await validate_chat_data(chat_data_parsed)

        stored_files = []

        for file in files:
            if file.content_type is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"File {file.filename} has no content type",
                )
            stored_files.append(f"{BASE_DIR}/{await file_store.save_file(file)}")

        image_files = [file for file in stored_files if Path(file).suffix.lower() in ALLOWED_IMAGE_EXTENSIONS]

        if len(image_files) > 0:
            return await inject_additional_attributes(
                lambda: chat_manager.generate_response(db_manager, last_message, image_files),
            )
        else:
            return await inject_additional_attributes(
                lambda: process_llm_response(request, chat_manager, str(last_message.content), messages),
            )

    @router.get("/chat_history", response_model=List[ChatHistorySchema])
    async def get_chat_history(
        user_id: str = Query(...),
        session_id: str = Query(...),
        db: AsyncSession = Depends(get_db),
    ):

        attributes = sdk_context.get_attributes(id, "llm", "agent_class", "tools", "instruction", "tool_retriever")
        llm_instance = attributes["agent_class"](
            attributes["llm"], attributes["tools"], attributes["instruction"], attributes["tool_retriever"]
        ).agent

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

        attributes = sdk_context.get_attributes(id, "llm", "agent_class", "tools", "instruction", "tool_retriever")
        llm_instance = attributes["agent_class"](
            attributes["llm"], attributes["tools"], attributes["instruction"], attributes["tool_retriever"]
        ).agent

        chat_manager = ChatManager(llm_instance, user_id=user_id, session_id="")
        db_manager = DatabaseManager(db)
        all_chats = await chat_manager.get_all_chats_for_user(db_manager)

        if not all_chats:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No chats found for this user",
            )

        return all_chats
