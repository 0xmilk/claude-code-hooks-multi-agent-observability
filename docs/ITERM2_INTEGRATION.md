# iTerm2 Integration Guide

This guide explains how to set up and use the iTerm2 terminal integration with the Multi-Agent Observability app.

## Overview

The iTerm2 integration allows you to:
- View all open iTerm2 terminal sessions in the web interface
- See real-time terminal output
- Send commands to terminals from the web interface
- Monitor multiple terminals simultaneously

## Prerequisites

1. **macOS** with iTerm2 installed
2. **iTerm2 Python API enabled**:
   - Open iTerm2 → Preferences → Magic
   - Check "Enable Python API"
   - Restart iTerm2
3. **Python 3.8+** installed
4. **Main application running** (via `./scripts/start-system.sh`)

## Installation

### 1. Install Python Dependencies

```bash
cd apps/iterm2-service
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Start the iTerm2 Service

```bash
./scripts/start-iterm2-service.sh
```

This will:
- Check that iTerm2 is running
- Create/activate Python virtual environment
- Install dependencies (first time only)
- Start the FastAPI service on port 4001

### 3. Access iTerm2 Features

1. Open the main app: http://localhost:5173
2. Click the terminal icon (🖥️) in the header
3. The iTerm2 terminal manager will open

## Using the Terminal Manager

### Terminal List (Left Panel)
- Shows all open iTerm2 sessions
- Displays:
  - Session name
  - Current directory
  - Running command (if any)
  - Window and tab information
- Click on a terminal to select it

### Terminal Viewer (Right Panel)
- Shows live terminal output
- Features:
  - **Auto-scroll**: Automatically scrolls to bottom on new output
  - **Clear**: Clears the display (client-side only)
  - **Command input**: Send commands to the selected terminal

### Keyboard Shortcuts
- `Ctrl+L`: Clear terminal display (client-side)

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐     ┌──────────┐
│   iTerm2    │────▶│ Python API   │────▶│  FastAPI    │────▶│ Vue App  │
│  Terminal   │     │  (iterm2)    │     │  Service    │     │ (Client) │
└─────────────┘     └──────────────┘     └─────────────┘     └──────────┘
                                               :4001              :5173
```

### Components

1. **iTerm2 Service** (`apps/iterm2-service/`)
   - Python FastAPI service
   - Connects to iTerm2 via Python API
   - Provides REST and WebSocket endpoints
   - Runs on port 4001

2. **Frontend Plugin** (`apps/client/src/plugins/iterm2/`)
   - Vue.js components
   - Terminal manager UI
   - WebSocket integration for live updates

## API Endpoints

### REST API
- `GET /api/terminals` - List all terminals
- `GET /api/terminals/{id}/content` - Get terminal content
- `POST /api/terminals/{id}/command` - Send command

### WebSocket
- `ws://localhost:4001/ws/terminals` - Terminal list updates
- `ws://localhost:4001/ws/terminals/{id}` - Live terminal output

## Security

- Service only accepts connections from local network IPs
- Same security model as main application
- No external access by default

## Troubleshooting

### "iTerm2 not connected"
- Ensure iTerm2 is running
- Check Python API is enabled in iTerm2 preferences
- Restart both iTerm2 and the service

### No terminals showing
- Open at least one terminal window in iTerm2
- Click "Refresh" in the terminal manager
- Check browser console for errors

### Port 4001 already in use
- Another instance might be running
- Kill existing process: `lsof -ti:4001 | xargs kill -9`
- Restart the service

### WebSocket connection failed
- Check that both services are running
- Verify firewall isn't blocking local connections
- Check browser console for specific errors

## Development

### Adding Features

The iTerm2 integration is designed as a modular plugin:

```
apps/
├── iterm2-service/     # Python backend
│   └── src/
│       ├── main.py     # FastAPI app
│       ├── iterm_api.py # iTerm2 wrapper
│       └── models.py   # Data models
│
└── client/
    └── src/
        └── plugins/
            └── iterm2/ # Frontend plugin
                ├── components/
                ├── composables/
                └── types.ts
```

### Future Enhancements

Potential features to add:
- Terminal session recording
- Multi-command scripting
- Terminal sharing/collaboration
- SSH session management
- Terminal theming sync
- Command history search
- Output filtering/search

## Credits

Built using:
- [iTerm2 Python API](https://iterm2.com/python-api/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Vue.js](https://vuejs.org/)