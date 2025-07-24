import { ref, computed, onMounted, onUnmounted } from 'vue';
import type { Terminal, TerminalContent, CommandRequest, CommandResponse, TerminalUpdate } from '../types';

const ITERM2_API_BASE = 'http://localhost:4001';

// Get dynamic host for network access
const getApiHost = () => {
  const host = window.location.hostname;
  if (host === 'localhost' || host === '127.0.0.1') {
    return 'localhost';
  }
  return host;
};

const ITERM2_API_URL = `http://${getApiHost()}:4001`;
const ITERM2_WS_URL = `ws://${getApiHost()}:4001`;

export function useTerminals() {
  const terminals = ref<Terminal[]>([]);
  const selectedTerminal = ref<Terminal | null>(null);
  const terminalContent = ref<Map<string, TerminalContent>>(new Map());
  const loading = ref(false);
  const error = ref<string | null>(null);
  const wsConnections = ref<Map<string, WebSocket>>(new Map());
  const terminalsWs = ref<WebSocket | null>(null);

  // Computed
  const sortedTerminals = computed(() => {
    return [...terminals.value].sort((a, b) => {
      // Sort by window, then tab, then name
      if (a.window_id !== b.window_id) {
        return a.window_id.localeCompare(b.window_id);
      }
      if (a.tab_id !== b.tab_id) {
        return a.tab_id.localeCompare(b.tab_id);
      }
      return a.name.localeCompare(b.name);
    });
  });

  // Fetch all terminals
  const fetchTerminals = async () => {
    loading.value = true;
    error.value = null;
    
    try {
      const response = await fetch(`${ITERM2_API_URL}/api/terminals`);
      if (!response.ok) {
        throw new Error(`Failed to fetch terminals: ${response.statusText}`);
      }
      
      terminals.value = await response.json();
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch terminals';
      console.error('Error fetching terminals:', err);
    } finally {
      loading.value = false;
    }
  };

  // Fetch terminal content
  const fetchTerminalContent = async (terminalId: string) => {
    try {
      const response = await fetch(`${ITERM2_API_URL}/api/terminals/${terminalId}/content`);
      if (!response.ok) {
        throw new Error(`Failed to fetch terminal content: ${response.statusText}`);
      }
      
      const content: TerminalContent = await response.json();
      terminalContent.value.set(terminalId, content);
    } catch (err) {
      console.error('Error fetching terminal content:', err);
    }
  };

  // Send command to terminal
  const sendCommand = async (request: CommandRequest): Promise<CommandResponse> => {
    try {
      const response = await fetch(
        `${ITERM2_API_URL}/api/terminals/${request.terminal_id}/command`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(request),
        }
      );
      
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to send command');
      }
      
      return await response.json();
    } catch (err) {
      throw err;
    }
  };

  // Connect to terminal WebSocket for live updates
  const connectToTerminal = (terminalId: string) => {
    // Don't reconnect if already connected
    if (wsConnections.value.has(terminalId)) {
      return;
    }

    const ws = new WebSocket(`${ITERM2_WS_URL}/ws/terminals/${terminalId}`);
    
    ws.onopen = () => {
      console.log(`Connected to terminal ${terminalId}`);
    };
    
    ws.onmessage = (event) => {
      try {
        const update: TerminalUpdate = JSON.parse(event.data);
        
        if (update.event_type === 'output') {
          // Update terminal content
          const content: TerminalContent = {
            terminal_id: terminalId,
            content: update.data.content,
            visible_content: update.data.content,
            cursor_position: update.data.cursor,
            has_more_history: false,
            timestamp: update.timestamp,
          };
          terminalContent.value.set(terminalId, content);
        }
      } catch (err) {
        console.error('Error parsing terminal update:', err);
      }
    };
    
    ws.onerror = (error) => {
      console.error(`WebSocket error for terminal ${terminalId}:`, error);
    };
    
    ws.onclose = () => {
      console.log(`Disconnected from terminal ${terminalId}`);
      wsConnections.value.delete(terminalId);
    };
    
    wsConnections.value.set(terminalId, ws);
  };

  // Disconnect from terminal WebSocket
  const disconnectFromTerminal = (terminalId: string) => {
    const ws = wsConnections.value.get(terminalId);
    if (ws) {
      ws.close();
      wsConnections.value.delete(terminalId);
    }
  };

  // Connect to terminals list WebSocket
  const connectToTerminalsList = () => {
    if (terminalsWs.value) {
      return;
    }

    const ws = new WebSocket(`${ITERM2_WS_URL}/ws/terminals`);
    
    ws.onopen = () => {
      console.log('Connected to terminals list WebSocket');
    };
    
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === 'terminals') {
          terminals.value = data.data;
        }
      } catch (err) {
        console.error('Error parsing terminals update:', err);
      }
    };
    
    ws.onerror = (error) => {
      console.error('Terminals WebSocket error:', error);
    };
    
    ws.onclose = () => {
      console.log('Disconnected from terminals list WebSocket');
      terminalsWs.value = null;
      // Attempt to reconnect after 5 seconds
      setTimeout(() => connectToTerminalsList(), 5000);
    };
    
    terminalsWs.value = ws;
  };

  // Select a terminal
  const selectTerminal = (terminal: Terminal | null) => {
    selectedTerminal.value = terminal;
    
    if (terminal) {
      // Fetch initial content
      fetchTerminalContent(terminal.id);
      // Connect to WebSocket for live updates
      connectToTerminal(terminal.id);
    }
  };

  // Lifecycle
  onMounted(() => {
    fetchTerminals();
    connectToTerminalsList();
  });

  onUnmounted(() => {
    // Close all WebSocket connections
    wsConnections.value.forEach((ws) => ws.close());
    wsConnections.value.clear();
    
    if (terminalsWs.value) {
      terminalsWs.value.close();
      terminalsWs.value = null;
    }
  });

  return {
    // State
    terminals,
    sortedTerminals,
    selectedTerminal,
    terminalContent,
    loading,
    error,
    
    // Methods
    fetchTerminals,
    fetchTerminalContent,
    sendCommand,
    selectTerminal,
    connectToTerminal,
    disconnectFromTerminal,
  };
}