# iTerm2 Service

Python service that provides API access to iTerm2 terminals for the Multi-Agent Observability app.

## Prerequisites

1. **iTerm2** with Python API enabled:
   - Open iTerm2 Preferences
   - Go to "Magic" section
   - Enable "Python API"
   - Restart iTerm2

2. **Python 3.8+** installed

## Installation

1. Create virtual environment:
```bash
cd apps/iterm2-service
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Service

1. Make sure iTerm2 is running
2. Start the service:
```bash
cd src
python -m uvicorn main:app --host 0.0.0.0 --port 4001 --reload
```

The service will be available at http://localhost:4001

## API Endpoints

### REST API

- `GET /health` - Health check
- `GET /api/terminals` - List all terminals
- `GET /api/terminals/{id}/content` - Get terminal content
- `POST /api/terminals/{id}/command` - Send command to terminal

### WebSocket

- `ws://localhost:4001/ws/terminals/{id}` - Real-time updates for specific terminal
- `ws://localhost:4001/ws/terminals` - Real-time terminal list updates

## Security

The service only accepts connections from local network IPs (same as main server).

## Architecture

This service acts as a bridge between iTerm2's Python API and the web application:

```
iTerm2 <-> Python API <-> FastAPI Service <-> Web App
```

## Troubleshooting

1. **"iTerm2 not connected" error**:
   - Make sure iTerm2 is running
   - Check that Python API is enabled in iTerm2 preferences
   - Restart both iTerm2 and the service

2. **Connection refused**:
   - Check that the service is running on port 4001
   - Verify firewall settings

3. **No terminals showing**:
   - Open at least one terminal window in iTerm2
   - Check iTerm2 Python API permissions