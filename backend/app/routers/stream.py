import uuid
from typing import Any, Dict

from bson import ObjectId
from fastapi import APIRouter, HTTPException, Request, WebSocket, WebSocketDisconnect, status
from loguru import logger
from pipecat.runner.types import WebSocketRunnerArguments

from app.bot import bot
from app.config import settings
from app.database import get_database

router = APIRouter()


@router.post("/connect")
async def bot_connect(request: Request) -> Dict[str, Any]:
    logger.info(f"Received connect request from {request.client.host if request.client else 'unknown'}")
    
    try:
        body: Dict[str, Any] = await request.json()
        logger.info(f"Parsed request body: {body}, body keys: {list(body.keys())}")    
    except Exception as e:
        try:
            body_content = await request.body()
            body_str = body_content.decode('utf-8', errors='ignore')[:200]
            logger.error(f"Failed to parse request body: {e}, body content (first 200 chars): {body_str}")
        except Exception:
            logger.error(f"Failed to parse request body: {e}, could not read body content")
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid JSON in request body: {str(e)}"
        )

    equipment_id: str = body.get("equipment_id", "")

    if not equipment_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="equipment_id is required",
        )

    db = get_database()

    try:
        equipment = await db.equipment.find_one({"_id": ObjectId(equipment_id)})
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid equipment_id format"
        )

    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Equipment {equipment_id} not found"
        )

    forworded_protocol = request.headers.get("x-forwarded-proto", "")

    if forworded_protocol:
        scheme = forworded_protocol
    else:
        scheme = request.url.scheme    


@router.websocket("/ws/{equipment_id}")
async def websocket_endpoint(websocket: WebSocket, equipment_id: str):
    await websocket.accept()
    logger.info(f"Connection accepted for equipment {equipment_id}")
    
    try:
        db = get_database()
        equipment = await db.equipment.find_one({"_id": ObjectId(equipment_id)})
        if not equipment:
            logger.error(f"Equipment {equipment_id} not found")
            await websocket.close(code=4004, reason="Equipment not found")
            return
        
        body = {
            "equipment_id": equipment_id,
            "tenant_id": settings.TENANT_ID,
            "session_id": str(uuid.uuid4()),
            "user_id": settings.USER_ID,
        } 
        
        await bot(WebSocketRunnerArguments(websocket=websocket, body=body, run_params=bot.run_params))

    except WebSocketDisconnect:
        logger.info("websocket Disconnected")
        
    except Exception as e:
        logger.error(f"websocket error {e}")
        try:
            await websocket.close(code=1011, reason=f"Internal server error {str(e)}")
        except Exception:
            logger.error("Failed to close websocket")
            pass