// Dynamic host configuration for local network access
const getApiHost = () => {
  // If we're accessing from a different device, use the actual host
  const host = window.location.hostname;
  
  // If we're on localhost/127.0.0.1, keep it as is for development
  if (host === 'localhost' || host === '127.0.0.1') {
    return 'localhost';
  }
  
  // Otherwise, use the actual host (e.g., 192.168.1.100)
  return host;
};

const API_HOST = getApiHost();
const API_PORT = 4000;

export const API_BASE_URL = `http://${API_HOST}:${API_PORT}`;
export const WS_URL = `ws://${API_HOST}:${API_PORT}/stream`;