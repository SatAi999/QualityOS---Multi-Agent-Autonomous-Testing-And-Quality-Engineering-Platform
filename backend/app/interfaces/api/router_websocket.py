import asyncio
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import redis.asyncio as ardis
from app.core.config import settings

router = APIRouter(prefix="/ws", tags=["WebSockets"])
logger = logging.getLogger("QualityOS.WebSocket")

@router.websocket("/jobs/{job_id}")
async def job_websocket_endpoint(websocket: WebSocket, job_id: str):
    """
    Subscribes to Redis channel events for a job run and streams live logs
    and agent state changes directly to the client browser.
    """
    await websocket.accept()
    logger.info(f"WebSocket client connected for job: {job_id}")
    
    r_client = ardis.from_url(settings.REDIS_URI)
    pubsub = r_client.pubsub()
    
    # Subscribe to job specific channel
    await pubsub.subscribe(f"job_events:{job_id}")
    
    async def listen_redis():
        try:
            async for message in pubsub.listen():
                if message["type"] == "message":
                    data = message["data"].decode("utf-8")
                    await websocket.send_text(data)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Error reading Redis subscription for job {job_id}: {str(e)}")

    redis_task = asyncio.create_task(listen_redis())
    
    try:
        # Keep connection open and check for client messages
        while True:
            # We don't expect messages from client, but we monitor for disconnects
            await websocket.receive_text()
    except WebSocketDisconnect:
        logger.info(f"WebSocket client disconnected for job: {job_id}")
    finally:
        redis_task.cancel()
        await pubsub.unsubscribe(f"job_events:{job_id}")
        await pubsub.close()
        await r_client.close()
