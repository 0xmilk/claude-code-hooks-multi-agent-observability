#!/bin/bash

# Add bun to PATH if it exists
if [ -d "$HOME/.bun/bin" ]; then
    export PATH="$HOME/.bun/bin:$PATH"
fi

echo "🚀 Starting Multi-Agent Observability System"
echo "==========================================="

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
# Get the project root directory (parent of scripts)
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

# Function to check if port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Check if ports are already in use
if check_port 4000; then
    echo -e "${YELLOW}⚠️  Port 4000 is already in use. Run ./scripts/reset-system.sh first.${NC}"
    exit 1
fi

if check_port 5173; then
    echo -e "${YELLOW}⚠️  Port 5173 is already in use. Run ./scripts/reset-system.sh first.${NC}"
    exit 1
fi

# Start server
echo -e "\n${GREEN}Starting server on port 4000...${NC}"
cd "$PROJECT_ROOT/apps/server"
bun run dev &
SERVER_PID=$!

# Wait for server to be ready
echo -e "${YELLOW}Waiting for server to start...${NC}"
for i in {1..10}; do
    if curl -s http://localhost:4000/health >/dev/null 2>&1 || curl -s http://localhost:4000/events/filter-options >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Server is ready!${NC}"
        break
    fi
    sleep 1
done

# Start client
echo -e "\n${GREEN}Starting client on port 5173...${NC}"
cd "$PROJECT_ROOT/apps/client"
bun run dev &
CLIENT_PID=$!

# Wait for client to be ready
echo -e "${YELLOW}Waiting for client to start...${NC}"
for i in {1..10}; do
    if curl -s http://localhost:5173 >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Client is ready!${NC}"
        break
    fi
    sleep 1
done

# Get local IP address
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    LOCAL_IP=$(ifconfig | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}' | head -n1)
else
    # Linux
    LOCAL_IP=$(hostname -I | awk '{print $1}')
fi

# Display status
echo -e "\n${BLUE}============================================${NC}"
echo -e "${GREEN}✅ Multi-Agent Observability System Started${NC}"
echo -e "${BLUE}============================================${NC}"
echo
echo -e "🖥️  Client URLs:"
echo -e "   Local:   ${GREEN}http://localhost:5173${NC}"
echo -e "   Network: ${GREEN}http://${LOCAL_IP}:5173${NC}"
echo
echo -e "🔌 Server API:"
echo -e "   Local:   ${GREEN}http://localhost:4000${NC}"
echo -e "   Network: ${GREEN}http://${LOCAL_IP}:4000${NC}"
echo
echo -e "📡 WebSocket:"
echo -e "   Local:   ${GREEN}ws://localhost:4000/stream${NC}"
echo -e "   Network: ${GREEN}ws://${LOCAL_IP}:4000/stream${NC}"
echo
echo -e "📝 Process IDs:"
echo -e "   Server PID: ${YELLOW}$SERVER_PID${NC}"
echo -e "   Client PID: ${YELLOW}$CLIENT_PID${NC}"
echo
echo -e "💡 To access from other devices on your network, use:"
echo -e "   ${GREEN}http://${LOCAL_IP}:5173${NC}"
echo
echo -e "To stop the system, run: ${YELLOW}./scripts/reset-system.sh${NC}"
echo -e "To test the system, run: ${YELLOW}./scripts/test-system.sh${NC}"
echo
echo -e "${BLUE}Press Ctrl+C to stop both processes${NC}"

# Function to cleanup on exit
cleanup() {
    echo -e "\n${YELLOW}Shutting down...${NC}"
    kill $SERVER_PID 2>/dev/null
    kill $CLIENT_PID 2>/dev/null
    echo -e "${GREEN}✅ Stopped all processes${NC}"
    exit 0
}

# Set up trap to cleanup on Ctrl+C
trap cleanup INT

# Wait for both processes
wait $SERVER_PID $CLIENT_PID