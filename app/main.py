from starlette.applications import Starlette
from starlette.responses import PlainTextResponse, HTMLResponse
from starlette.routing import Route, WebSocketRoute
from starlette.websockets import WebSocket, WebSocketDisconnect
from starlette.templating import Jinja2Templates
from pathlib import Path

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


BASE_DIR = Path(__file__).parent
TEMPLATES = Jinja2Templates(directory=str(BASE_DIR / "htmldirectory"))

async def index(request):
    return TEMPLATES.TemplateResponse(
        "index.html", 
        {"request": request, "page_title": "Starlette Echo Client"}
    )


async def websocket_endpoint(websocket: WebSocket):
    """
    Handles WebSocket connections, accepting messages and echoing them back.
    """
    await websocket.accept()
    client_id = f"{websocket.client.host}:{websocket.client.port}"
    logger.info(f"Client connected: {client_id}")
    
    await websocket.send_text(f"Connected to Starlette Echo Server! Your ID: {client_id}")

    try:
        while True:
            message = await websocket.receive_text()
            response_text = f"Server Echo: {message}"
            logger.info(f"Received from {client_id}: {message}")
            await websocket.send_text(response_text)

    except WebSocketDisconnect:
        logger.warning(f"Client disconnected: {client_id}")
    except Exception as e:
        logger.error(f"An error occurred with client {client_id}: {e}")
    finally:
        await websocket.close()


routes = [
    Route("/", index),
    WebSocketRoute("/ws", websocket_endpoint)
]

app = Starlette(routes=routes)
