import os
import httpx 

from datetime import datetime
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, HTTPException, Request, Header
from fastapi.responses import JSONResponse
from typing import Any, Dict, Optional

load_dotenv()

router = APIRouter(prefix="/api/py/webhook", tags=['webhooks'])

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET")

TG_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

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

class WebhookBody(BaseModel):
    url: str  # e.g., https://<your-ngrok>.ngrok.io/telegram/webhook

async def tg_send_message(chat_id: int, text: str) -> None:
    async with httpx.AsyncClient(timeout=10) as client:
        await client.post(f"{TG_API}/sendMessage", json={"chat_id": chat_id, "text": text})

@router.post("")
async def telegram_webhook(request: Request):
    # 1) Verify Telegram’s secret token (you’ll pass this when setting the webhook)
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

# --- Helpers to manage webhook without leaving FastAPI --
@router.post("/admin/set-webhook")
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

@router.post("/admin/delete-webhook")
async def delete_webhook():
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.post(f"{TG_API}/deleteWebhook", data={"drop_pending_updates": True})
    return JSONResponse(r.json())

@router.get("/admin/get-webhook-info")
async def get_webhook_info():
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(f"{TG_API}/getWebhookInfo")
    return JSONResponse(r.json())
