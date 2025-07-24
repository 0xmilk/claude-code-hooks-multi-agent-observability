"""Data models for iTerm2 integration."""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime


class Terminal(BaseModel):
    """Represents an iTerm2 terminal session."""
    id: str
    name: str
    window_id: str
    window_title: str
    tab_id: str
    tab_title: str
    current_directory: str
    command: Optional[str] = None
    pid: Optional[int] = None
    rows: int
    columns: int
    created_at: datetime
    last_activity: datetime
    is_active: bool = True


class TerminalContent(BaseModel):
    """Terminal output content."""
    terminal_id: str
    content: str
    visible_content: str
    cursor_position: Dict[str, int]
    has_more_history: bool
    timestamp: datetime


class CommandRequest(BaseModel):
    """Request to send a command to a terminal."""
    terminal_id: str
    command: str
    newline: bool = True


class CommandResponse(BaseModel):
    """Response after sending a command."""
    terminal_id: str
    command: str
    success: bool
    timestamp: datetime
    error: Optional[str] = None


class TerminalUpdate(BaseModel):
    """Real-time terminal update event."""
    terminal_id: str
    event_type: str  # 'output', 'status', 'closed'
    data: Dict[str, Any]
    timestamp: datetime