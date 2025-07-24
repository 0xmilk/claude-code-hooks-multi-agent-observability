<template>
  <div class="terminal-manager h-full flex flex-col bg-[var(--theme-bg-secondary)]">
    <!-- Header -->
    <div class="bg-[var(--theme-bg-primary)] border-b border-[var(--theme-border-primary)] p-4">
      <div class="flex items-center justify-between">
        <h2 class="text-xl font-bold text-[var(--theme-text-primary)]">
          iTerm2 Terminals
        </h2>
        <button
          @click="fetchTerminals"
          :disabled="loading"
          class="px-3 py-1.5 bg-[var(--theme-primary)] hover:bg-[var(--theme-primary-hover)] text-white rounded-md transition-colors disabled:opacity-50"
        >
          <span v-if="loading">🔄 Loading...</span>
          <span v-else>🔄 Refresh</span>
        </button>
      </div>
      
      <!-- Error message -->
      <div v-if="error" class="mt-2 p-2 bg-red-500/10 border border-red-500/30 rounded-md">
        <p class="text-sm text-red-400">{{ error }}</p>
      </div>
    </div>

    <!-- Content -->
    <div class="flex-1 flex overflow-hidden">
      <!-- Terminal List -->
      <div class="w-80 border-r border-[var(--theme-border-primary)] overflow-y-auto">
        <div v-if="sortedTerminals.length === 0" class="p-4 text-[var(--theme-text-secondary)] text-center">
          <p v-if="loading">Loading terminals...</p>
          <p v-else>No terminals found. Make sure iTerm2 is running and has open sessions.</p>
        </div>
        
        <div v-else class="p-2 space-y-2">
          <div
            v-for="terminal in sortedTerminals"
            :key="terminal.id"
            @click="selectTerminal(terminal)"
            :class="[
              'p-3 rounded-lg cursor-pointer transition-all',
              selectedTerminal?.id === terminal.id
                ? 'bg-[var(--theme-primary)] text-white'
                : 'bg-[var(--theme-bg-tertiary)] hover:bg-[var(--theme-bg-quaternary)] text-[var(--theme-text-primary)]'
            ]"
          >
            <div class="font-medium">{{ terminal.name }}</div>
            <div class="text-sm opacity-75 mt-1">
              <div>📁 {{ terminal.current_directory }}</div>
              <div v-if="terminal.command">🖥️ {{ terminal.command }}</div>
              <div class="text-xs mt-1">
                Window: {{ terminal.window_title }} | Tab: {{ terminal.tab_title }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Terminal Viewer -->
      <div class="flex-1 overflow-hidden">
        <TerminalViewer 
          v-if="selectedTerminal"
          :terminal="selectedTerminal"
          :content="terminalContent.get(selectedTerminal.id)"
          @send-command="handleSendCommand"
        />
        <div v-else class="h-full flex items-center justify-center text-[var(--theme-text-secondary)]">
          <p>Select a terminal to view its content</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useTerminals } from '../composables/useTerminals';
import TerminalViewer from './TerminalViewer.vue';
import type { CommandRequest } from '../types';

const {
  sortedTerminals,
  selectedTerminal,
  terminalContent,
  loading,
  error,
  fetchTerminals,
  selectTerminal,
  sendCommand,
} = useTerminals();

const handleSendCommand = async (command: string) => {
  if (!selectedTerminal.value) return;
  
  try {
    const request: CommandRequest = {
      terminal_id: selectedTerminal.value.id,
      command,
      newline: true,
    };
    
    const response = await sendCommand(request);
    if (!response.success) {
      console.error('Failed to send command:', response.error);
    }
  } catch (err) {
    console.error('Error sending command:', err);
  }
};
</script>

<style scoped>
.terminal-manager {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}
</style>