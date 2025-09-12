import os
import httpx 
import uvicorn
import ngrok

from contextlib import asynccontextmanager
from datetime import datetime
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from fastapi import FastAPI, Request, Header, HTTPException
from fastapi.responses import JSONResponse
from typing import Any, Dict, Optional

from api.utils.logger_config import setup_logger

load_dotenv()

CWD = os.getcwd()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")
NGROK_AUTH_TOKEN = os.getenv("NGROK_AUTH")
PORT = int(os.getenv("PORT", 5000))

TG_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

logger = setup_logger(f"{"isik-wo-log"}", log_dir=f'{CWD}/api/utils/logs')

# Initialize FastAPI app
app = FastAPI(
    title="ISIK WO TRACKER",
    version="1.0.0",
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

@app.post("/webhook")
async def telegram_webhook(request: Request, x_telegram_bot_api_secret_token: Optional[str] = Header(None)):
    # 1) Verify Telegram’s secret token (you’ll pass this when setting the webhook)
    if WEBHOOK_SECRET and x_telegram_bot_api_secret_token != WEBHOOK_SECRET:
        raise HTTPException(status_code=401, detail="Invalid secret token")

    # 2) Parse update
    data: Dict[str, Any] = await request.json()
    try:
        update = Update(**data)
    except Exception:
        # Always ACK quickly; Telegram expects 200-OK
        return JSONResponse({"ok": True})

    msg = update.message or update.edited_message
    if msg and msg.text:
        text = msg.text.strip()
        chat_id = msg.chat.id

        if text.startswith("/start"):
            await tg_send_message(chat_id, "Hi! Your webhook is alive ✨")
        else:
            await tg_send_message(chat_id, f"You said: {text}")

    # 3) ACK
    return JSONResponse({"ok": True})

# --- Helpers to manage webhook without leaving FastAPI ---

class WebhookBody(BaseModel):
    url: str  # e.g., https://<your-ngrok>.ngrok.io/telegram/webhook

@app.post("/admin/set-webhook")
async def set_webhook(body: WebhookBody):
    payload = {
        "url": body.url,
        "secret_token": WEBHOOK_SECRET,
        "drop_pending_updates": True,
        # Optional: restrict allowed updates
        # "allowed_updates": ["message", "edited_message"]
    }
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.post(f"{TG_API}/setWebhook", data=payload)
    return JSONResponse(r.json())

@app.post("/admin/delete-webhook")
async def delete_webhook():
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.post(f"{TG_API}/deleteWebhook", data={"drop_pending_updates": True})
    return JSONResponse(r.json())

@app.get("/admin/get-webhook-info")
async def get_webhook_info():
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(f"{TG_API}/getWebhookInfo")
    return JSONResponse(r.json())

if __name__ == "__main__":
    # Run the server
    uvicorn.run(
        "main:app",  # Change "main" to your filename if different
        host="127.0.0.1",
        port=PORT,
        reload=True  # Enable auto-reload for development
    )