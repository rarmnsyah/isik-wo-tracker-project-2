import os
import httpx 
import uvicorn

from datetime import datetime
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from fastapi import FastAPI, Request, Header, HTTPException
from fastapi.responses import JSONResponse
from typing import Any, Dict, Optional

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")
WEBHOOK_PATH = os.getenv("WEBHOOK_PATH", "/telegram/webhook")
PORT = int(os.getenv("PORT", "8000"))

TG_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

# Initialize FastAPI app
app = FastAPI(
    title="FastAPI Get Started App",
    description="A comprehensive starter application demonstrating FastAPI features",
    version="1.0.0"
)

class Chat(BaseModel):
    id: int

class Message(BaseModel):
    message_id: int
    chat: Chat
    text: Optional[str] = None

class Update(BaseModel):
    update_id: int
    message: Optional[Message] = None
    edited_message: Optional[Message] = None

class MessageResponse(BaseModel):
    message: str
    timestamp: datetime

@app.get("/", response_model=MessageResponse)
async def root():
    """Welcome endpoint"""
    return MessageResponse(
        message="Welcome to FastAPI Get Started App! Visit /docs for API documentation.",
        timestamp=datetime.now()
    )


async def tg_send_message(chat_id: int, text: str) -> None:
    async with httpx.AsyncClient(timeout=10) as client:
        await client.post(f"{TG_API}/sendMessage", json={"chat_id": chat_id, "text": text})

if __name__ == "__main__":
    # Run the server
    uvicorn.run(
        "main:app",  # Change "main" to your filename if different
        host="0.0.0.0",
        port=8000,
        reload=True  # Enable auto-reload for development
    )