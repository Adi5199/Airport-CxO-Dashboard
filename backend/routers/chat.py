from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime
import json

from backend.ai.prompts import DEMO_PROMPTS, QUICK_QUERIES

router = APIRouter(prefix="/api/chat", tags=["chat"])


class ChatRequest(BaseModel):
    query: str
    date: Optional[str] = None
    conversation_history: Optional[List[Dict]] = None


@router.post("")
async def chat_stream(request: Request, body: ChatRequest):
    chatbot = request.app.state.chatbot
    config = request.app.state.config

    date = datetime.strptime(body.date, "%Y-%m-%d") if body.date else datetime.strptime(config["data"]["report_date"], "%Y-%m-%d")

    def generate():
        full_response = ""
        for chunk in chatbot.chat_stream(body.query, date=date, history=body.conversation_history):
            full_response += chunk
            yield f"data: {json.dumps({'token': chunk})}\n\n"
        yield f"data: {json.dumps({'done': True, 'full_response': full_response})}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


@router.post("/non-streaming")
async def chat_non_streaming(request: Request, body: ChatRequest):
    chatbot = request.app.state.chatbot
    config = request.app.state.config

    date = datetime.strptime(body.date, "%Y-%m-%d") if body.date else datetime.strptime(config["data"]["report_date"], "%Y-%m-%d")

    response = chatbot.chat(body.query, date=date, history=body.conversation_history)
    has_api = chatbot.client is not None

    return {"response": response, "mode": "openai" if has_api else "fallback"}


@router.get("/demo-prompts")
def get_demo_prompts():
    prompts = []
    for key, val in DEMO_PROMPTS.items():
        prompts.append({"key": key, "label": val["label"], "prompt": val["prompt"]})
    return {"prompts": prompts}


@router.get("/quick-queries")
def get_quick_queries():
    return {"queries": QUICK_QUERIES}
