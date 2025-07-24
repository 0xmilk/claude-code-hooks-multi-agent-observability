#!/bin/bash

# Start script for iTerm2 Python service

echo "🚀 Starting iTerm2 Service"
echo "=========================="

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
# Get the project root directory (parent of scripts)
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"
ITERM2_SERVICE_DIR="$PROJECT_ROOT/apps/iterm2-service"

# Check if iTerm2 is running
if ! pgrep -x "iTerm2" > /dev/null; then
    echo -e "${YELLOW}⚠️  iTerm2 is not running. Please start iTerm2 first.${NC}"
    echo -e "${YELLOW}   The service requires iTerm2 to be running with Python API enabled.${NC}"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "$ITERM2_SERVICE_DIR/venv" ]; then
    echo -e "${YELLOW}Creating Python virtual environment...${NC}"
    cd "$ITERM2_SERVICE_DIR"
    python3 -m venv venv
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Failed to create virtual environment${NC}"
        exit 1
    fi
fi

# Activate virtual environment
echo -e "${BLUE}Activating virtual environment...${NC}"
source "$ITERM2_SERVICE_DIR/venv/bin/activate"

# Install dependencies if not already installed
if ! pip show iterm2 > /dev/null 2>&1; then
    echo -e "${YELLOW}Installing Python dependencies...${NC}"
    pip install -r "$ITERM2_SERVICE_DIR/requirements.txt"
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Failed to install dependencies${NC}"
        exit 1
    fi
fi

# Function to check if port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Check if port 4001 is already in use
if check_port 4001; then
    echo -e "${YELLOW}⚠️  Port 4001 is already in use.${NC}"
    echo -e "${YELLOW}   The iTerm2 service might already be running.${NC}"
    exit 1
fi

# Get local IP address
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    LOCAL_IP=$(ifconfig | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}' | head -n1)
else
    # Linux
    LOCAL_IP=$(hostname -I | awk '{print $1}')
fi

# Start the service
echo -e "\n${GREEN}Starting iTerm2 service on port 4001...${NC}"
cd "$ITERM2_SERVICE_DIR/src"

# Run with uvicorn
python -m uvicorn main:app --host 0.0.0.0 --port 4001 --reload &
SERVICE_PID=$!

# Wait for service to be ready
echo -e "${YELLOW}Waiting for service to start...${NC}"
for i in {1..10}; do
    if curl -s http://localhost:4001/health >/dev/null 2>&1; then
        echo -e "${GREEN}✅ iTerm2 service is ready!${NC}"
        break
    fi
    sleep 1
done

# Display status
echo -e "\n${BLUE}============================================${NC}"
echo -e "${GREEN}✅ iTerm2 Service Started${NC}"
echo -e "${BLUE}============================================${NC}"
echo
echo -e "🖥️  iTerm2 API URLs:"
echo -e "   Local:   ${GREEN}http://localhost:4001${NC}"
echo -e "   Network: ${GREEN}http://${LOCAL_IP}:4001${NC}"
echo
echo -e "📡 WebSocket URLs:"
echo -e "   Terminals List: ${GREEN}ws://${LOCAL_IP}:4001/ws/terminals${NC}"
echo -e "   Terminal Stream: ${GREEN}ws://${LOCAL_IP}:4001/ws/terminals/{id}${NC}"
echo
echo -e "📝 Service PID: ${YELLOW}$SERVICE_PID${NC}"
echo
echo -e "${BLUE}Press Ctrl+C to stop the service${NC}"

# Function to cleanup on exit
cleanup() {
    echo -e "\n${YELLOW}Shutting down iTerm2 service...${NC}"
    kill $SERVICE_PID 2>/dev/null
    echo -e "${GREEN}✅ Service stopped${NC}"
    exit 0
}

# Set up trap to cleanup on Ctrl+C
trap cleanup INT

# Wait for the process
wait $SERVICE_PID