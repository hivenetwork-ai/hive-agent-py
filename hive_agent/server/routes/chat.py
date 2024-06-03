from typing import List

from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import StreamingResponse
from llama_index.core.llms import ChatMessage
from llama_index.core.llms import MessageRole

from pydantic import BaseModel

from hive_agent.config import Config
class Message(BaseModel):
    role: MessageRole
    content: str


class ChatData(BaseModel):
    messages: List[Message]


def setup_chat_routes(router: APIRouter, agent):

    @router.post("/chat")
    async def chat(request: Request, data: ChatData):
        if len(data.messages) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No messages provided",
            )

        last_message = data.messages.pop()
        if last_message.role != MessageRole.USER:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Last message must be from user",
            )

        # convert messages coming from the request to type ChatMessage
        messages = [ChatMessage(role=m.role, content=m.content) for m in data.messages]
        config = Config()
        model = config.get("model", "model", "gpt-3.5-turbo")
        if "gpt" in model:
            response = await agent.astream_chat(last_message.content, messages)
        else:
            response = await agent.achat(last_message.content, messages)

        async def event_generator():
            async for token in response.async_response_gen():
                if await request.is_disconnected():
                    break
                yield token
        if "gpt" in model:
            return StreamingResponse(event_generator(), media_type="text/plain")
        else:
            return response
