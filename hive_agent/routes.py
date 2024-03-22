from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import StreamingResponse
from llama_index.agent.openai import OpenAIAgent
from llama_index.core.llms import ChatMessage, MessageRole

from hive_agent.api_models import ChatData


def setup_routes(app: FastAPI, agent: OpenAIAgent):
    @app.get("/")
    def read_root():
        return "Hive Agent is running"

    @app.post("/api/chat")
    async def handle_chat(request: Request, data: ChatData):
        # check preconditions and get last message
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
        messages = [
            ChatMessage(
                role=m.role,
                content=m.content,
            )
            for m in data.messages
        ]

        # query chat engine
        response = await agent.astream_chat(last_message.content, messages)

        # stream response
        async def event_generator():
            async for token in response.async_response_gen():
                # if client closes connection, stop sending events
                if await request.is_disconnected():
                    break
                yield token

        return StreamingResponse(event_generator(), media_type="text/plain")
