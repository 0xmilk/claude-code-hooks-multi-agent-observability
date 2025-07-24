"""iTerm2 API wrapper for terminal management."""
import iterm2
import asyncio
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

from .models import Terminal, TerminalContent, CommandResponse

logger = logging.getLogger(__name__)


class ITermAPI:
    """Wrapper for iTerm2 Python API."""
    
    def __init__(self):
        self.connection: Optional[iterm2.Connection] = None
        self.app: Optional[iterm2.App] = None
        self._screen_streamers: Dict[str, Any] = {}
        self._update_callbacks = []
        
    async def connect(self):
        """Establish connection to iTerm2."""
        try:
            self.connection = await iterm2.Connection.async_create()
            self.app = await iterm2.async_get_app(self.connection)
            logger.info("Connected to iTerm2")
        except Exception as e:
            logger.error(f"Failed to connect to iTerm2: {e}")
            raise
            
    async def disconnect(self):
        """Close connection to iTerm2."""
        if self.connection:
            # Stop all screen streamers
            for session_id in list(self._screen_streamers.keys()):
                await self.stop_streaming(session_id)
            # Note: iterm2.Connection doesn't have a close method in newer versions
            self.connection = None
            self.app = None
            logger.info("Disconnected from iTerm2")
            
    async def get_all_terminals(self) -> List[Terminal]:
        """Get all terminal sessions."""
        if not self.app:
            raise RuntimeError("Not connected to iTerm2")
            
        terminals = []
        for window in self.app.windows:
            window_title = await window.async_get_title()
            window_id = window.window_id
            
            for tab in window.tabs:
                tab_title = await tab.async_get_title()
                tab_id = tab.tab_id
                
                for session in tab.sessions:
                    try:
                        name = await session.async_get_variable("session.name") or "Unnamed"
                        cwd = await session.async_get_variable("session.path") or "/"
                        command = await session.async_get_variable("session.command")
                        pid = await session.async_get_variable("session.pid")
                        
                        # Get grid size
                        grid = await session.async_get_grid_size()
                        
                        terminal = Terminal(
                            id=session.session_id,
                            name=name,
                            window_id=window_id,
                            window_title=window_title,
                            tab_id=tab_id,
                            tab_title=tab_title,
                            current_directory=cwd,
                            command=command,
                            pid=int(pid) if pid else None,
                            rows=grid.height,
                            columns=grid.width,
                            created_at=datetime.now(),  # iTerm2 doesn't provide creation time
                            last_activity=datetime.now(),
                            is_active=True
                        )
                        terminals.append(terminal)
                    except Exception as e:
                        logger.error(f"Error getting session info: {e}")
                        continue
                        
        return terminals
        
    async def get_terminal_content(self, session_id: str) -> Optional[TerminalContent]:
        """Get current content of a terminal."""
        session = self._get_session_by_id(session_id)
        if not session:
            return None
            
        try:
            # Get screen contents
            contents = await session.async_get_screen_contents()
            
            # Get visible text
            visible_lines = []
            for i in range(contents.number_of_lines):
                line = contents.line(i)
                visible_lines.append(line.string)
            visible_content = "\n".join(visible_lines)
            
            # Get cursor position
            cursor = contents.cursor
            
            # Check if there's history
            line_info = await session.async_get_line_info()
            
            return TerminalContent(
                terminal_id=session_id,
                content=visible_content,  # For now, just visible content
                visible_content=visible_content,
                cursor_position={
                    "x": cursor.x,
                    "y": cursor.y
                },
                has_more_history=line_info.overflow > 0,
                timestamp=datetime.now()
            )
        except Exception as e:
            logger.error(f"Error getting terminal content: {e}")
            return None
            
    async def send_command(self, session_id: str, command: str, newline: bool = True) -> CommandResponse:
        """Send a command to a terminal."""
        session = self._get_session_by_id(session_id)
        if not session:
            return CommandResponse(
                terminal_id=session_id,
                command=command,
                success=False,
                timestamp=datetime.now(),
                error="Session not found"
            )
            
        try:
            text = command + "\n" if newline else command
            await session.async_send_text(text)
            
            return CommandResponse(
                terminal_id=session_id,
                command=command,
                success=True,
                timestamp=datetime.now()
            )
        except Exception as e:
            logger.error(f"Error sending command: {e}")
            return CommandResponse(
                terminal_id=session_id,
                command=command,
                success=False,
                timestamp=datetime.now(),
                error=str(e)
            )
            
    async def start_streaming(self, session_id: str, callback):
        """Start streaming updates from a terminal."""
        session = self._get_session_by_id(session_id)
        if not session or session_id in self._screen_streamers:
            return
            
        async def stream_handler():
            async with session.get_screen_streamer() as streamer:
                self._screen_streamers[session_id] = streamer
                while session_id in self._screen_streamers:
                    try:
                        contents = await streamer.async_get()
                        await callback(session_id, contents)
                    except asyncio.CancelledError:
                        break
                    except Exception as e:
                        logger.error(f"Error in screen streamer: {e}")
                        break
                        
        asyncio.create_task(stream_handler())
        
    async def stop_streaming(self, session_id: str):
        """Stop streaming updates from a terminal."""
        if session_id in self._screen_streamers:
            del self._screen_streamers[session_id]
            
    def _get_session_by_id(self, session_id: str) -> Optional[iterm2.Session]:
        """Find a session by its ID."""
        if not self.app:
            return None
            
        for window in self.app.windows:
            for tab in window.tabs:
                for session in tab.sessions:
                    if session.session_id == session_id:
                        return session
        return None
        
    def add_update_callback(self, callback):
        """Add a callback for terminal updates."""
        self._update_callbacks.append(callback)
        
    def remove_update_callback(self, callback):
        """Remove an update callback."""
        if callback in self._update_callbacks:
            self._update_callbacks.remove(callback)