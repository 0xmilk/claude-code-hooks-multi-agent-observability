"""FastAPI server for iTerm2 integration."""
import asyncio
import logging
from contextlib import asynccontextmanager
from typing import List, Optional, Dict, Any
from datetime import datetime

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from .models import (
    Terminal, TerminalContent, CommandRequest, 
    CommandResponse, TerminalUpdate
)
from .iterm_api import ITermAPI

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global iTerm2 API instance
iterm_api = ITermAPI()

# WebSocket connections
websocket_clients: List[WebSocket] = []


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle."""
    # Startup
    logger.info("Starting iTerm2 service...")
    try:
        await iterm_api.connect()
        logger.info("Connected to iTerm2")
    except Exception as e:
        logger.error(f"Failed to connect to iTerm2: {e}")
        # Continue anyway, connection can be retried
    
    yield
    
    # Shutdown
    logger.info("Shutting down iTerm2 service...")
    await iterm_api.disconnect()


# Create FastAPI app
app = FastAPI(
    title="iTerm2 Service",
    description="API for iTerm2 terminal integration",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS for local network only
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://192.168.*.*:5173",
        "http://10.*.*.*:5173",
        "http://172.16.*.*:5173",
        "http://172.17.*.*:5173",
        "http://172.18.*.*:5173",
        "http://172.19.*.*:5173",
        "http://172.20.*.*:5173",
        "http://172.21.*.*:5173",
        "http://172.22.*.*:5173",
        "http://172.23.*.*:5173",
        "http://172.24.*.*:5173",
        "http://172.25.*.*:5173",
        "http://172.26.*.*:5173",
        "http://172.27.*.*:5173",
        "http://172.28.*.*:5173",
        "http://172.29.*.*:5173",
        "http://172.30.*.*:5173",
        "http://172.31.*.*:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "connected_to_iterm2": iterm_api.connection is not None,
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/terminals", response_model=List[Terminal])
async def get_terminals():
    """Get all available terminals."""
    if not iterm_api.connection:
        try:
            await iterm_api.connect()
        except Exception as e:
            raise HTTPException(status_code=503, detail="iTerm2 not connected")
    
    try:
        terminals = await iterm_api.get_all_terminals()
        return terminals
    except Exception as e:
        logger.error(f"Error getting terminals: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/terminals/{terminal_id}/content", response_model=TerminalContent)
async def get_terminal_content(terminal_id: str):
    """Get current content of a specific terminal."""
    if not iterm_api.connection:
        raise HTTPException(status_code=503, detail="iTerm2 not connected")
    
    content = await iterm_api.get_terminal_content(terminal_id)
    if not content:
        raise HTTPException(status_code=404, detail="Terminal not found")
    
    return content


@app.post("/api/terminals/{terminal_id}/command", response_model=CommandResponse)
async def send_command(terminal_id: str, request: CommandRequest):
    """Send a command to a specific terminal."""
    if not iterm_api.connection:
        raise HTTPException(status_code=503, detail="iTerm2 not connected")
    
    response = await iterm_api.send_command(
        terminal_id, 
        request.command, 
        request.newline
    )
    
    if not response.success:
        raise HTTPException(status_code=400, detail=response.error)
    
    return response


@app.websocket("/ws/terminals/{terminal_id}")
async def terminal_websocket(websocket: WebSocket, terminal_id: str):
    """WebSocket endpoint for real-time terminal updates."""
    await websocket.accept()
    websocket_clients.append(websocket)
    
    # Callback for terminal updates
    async def update_callback(session_id: str, contents):
        if session_id != terminal_id:
            return
            
        try:
            # Convert screen contents to simple format
            lines = []
            for i in range(contents.number_of_lines):
                line = contents.line(i)
                lines.append(line.string)
            
            update = TerminalUpdate(
                terminal_id=terminal_id,
                event_type="output",
                data={
                    "content": "\n".join(lines),
                    "cursor": {
                        "x": contents.cursor.x,
                        "y": contents.cursor.y
                    }
                },
                timestamp=datetime.now()
            )
            
            await websocket.send_json(update.dict())
        except Exception as e:
            logger.error(f"Error sending update: {e}")
    
    try:
        # Start streaming terminal content
        await iterm_api.start_streaming(terminal_id, update_callback)
        
        # Keep connection alive
        while True:
            try:
                await websocket.receive_text()
            except WebSocketDisconnect:
                break
                
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        # Stop streaming
        await iterm_api.stop_streaming(terminal_id)
        
        # Remove from clients list
        if websocket in websocket_clients:
            websocket_clients.remove(websocket)


@app.websocket("/ws/terminals")
async def terminals_websocket(websocket: WebSocket):
    """WebSocket endpoint for terminal list updates."""
    await websocket.accept()
    websocket_clients.append(websocket)
    
    try:
        # Send initial terminal list
        terminals = await iterm_api.get_all_terminals()
        await websocket.send_json({
            "type": "terminals",
            "data": [t.dict() for t in terminals]
        })
        
        # Keep connection alive and send periodic updates
        while True:
            try:
                # Wait for any message or timeout after 5 seconds
                await asyncio.wait_for(websocket.receive_text(), timeout=5.0)
            except asyncio.TimeoutError:
                # Send updated terminal list
                try:
                    terminals = await iterm_api.get_all_terminals()
                    await websocket.send_json({
                        "type": "terminals",
                        "data": [t.dict() for t in terminals]
                    })
                except Exception as e:
                    logger.error(f"Error getting terminals: {e}")
            except WebSocketDisconnect:
                break
                
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        if websocket in websocket_clients:
            websocket_clients.remove(websocket)


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",  # Listen on all interfaces for local network
        port=4001,       # Different port from main server
        reload=True,
        log_level="info"
    )