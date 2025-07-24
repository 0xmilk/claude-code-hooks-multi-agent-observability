/**
 * Types for iTerm2 integration
 */

export interface Terminal {
  id: string;
  name: string;
  window_id: string;
  window_title: string;
  tab_id: string;
  tab_title: string;
  current_directory: string;
  command?: string;
  pid?: number;
  rows: number;
  columns: number;
  created_at: string;
  last_activity: string;
  is_active: boolean;
}

export interface TerminalContent {
  terminal_id: string;
  content: string;
  visible_content: string;
  cursor_position: {
    x: number;
    y: number;
  };
  has_more_history: boolean;
  timestamp: string;
}

export interface CommandRequest {
  terminal_id: string;
  command: string;
  newline?: boolean;
}

export interface CommandResponse {
  terminal_id: string;
  command: string;
  success: boolean;
  timestamp: string;
  error?: string;
}

export interface TerminalUpdate {
  terminal_id: string;
  event_type: 'output' | 'status' | 'closed';
  data: Record<string, any>;
  timestamp: string;
}