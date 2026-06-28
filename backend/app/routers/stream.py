import uuid
from typing import Dict, Any
from fastapi import APIRouter, Request, HTTPException, status,WebSocket,WebSocketDisconnect,BackgroundTasks

from loguru import logger
import asyncio
from app.services.chat_services import ask_chatgpt_sse,process_text_chunk