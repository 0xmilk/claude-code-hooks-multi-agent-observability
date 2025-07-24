<template>
  <div class="terminal-viewer h-full flex flex-col bg-black">
    <!-- Terminal Header -->
    <div class="bg-gray-800 border-b border-gray-700 px-4 py-2 flex items-center justify-between">
      <div class="text-sm text-gray-300">
        <span class="font-medium">{{ terminal.name }}</span>
        <span class="text-gray-500 ml-2">{{ terminal.rows }}x{{ terminal.columns }}</span>
      </div>
      <div class="flex items-center space-x-2">
        <button
          @click="autoScroll = !autoScroll"
          :class="[
            'px-2 py-1 text-xs rounded transition-colors',
            autoScroll 
              ? 'bg-green-600 text-white' 
              : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
          ]"
        >
          Auto-scroll: {{ autoScroll ? 'ON' : 'OFF' }}
        </button>
        <button
          @click="clearTerminal"
          class="px-2 py-1 text-xs bg-gray-700 text-gray-300 hover:bg-gray-600 rounded transition-colors"
        >
          Clear
        </button>
      </div>
    </div>

    <!-- Terminal Content -->
    <div 
      ref="terminalContentRef"
      class="flex-1 overflow-y-auto p-2 font-mono text-sm text-gray-100"
      style="background-color: #000000;"
    >
      <pre v-if="content" class="whitespace-pre-wrap">{{ content.visible_content }}</pre>
      <div v-else class="text-gray-600 text-center mt-4">
        Connecting to terminal...
      </div>
    </div>

    <!-- Command Input -->
    <div class="bg-gray-900 border-t border-gray-700 p-2">
      <form @submit.prevent="sendCommand" class="flex space-x-2">
        <input
          v-model="commandInput"
          type="text"
          placeholder="Enter command..."
          class="flex-1 bg-gray-800 text-gray-100 px-3 py-2 rounded border border-gray-700 focus:outline-none focus:border-blue-500"
          :disabled="!terminal.is_active"
        />
        <button
          type="submit"
          :disabled="!commandInput.trim() || !terminal.is_active"
          class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Send
        </button>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, nextTick, onMounted, onUnmounted } from 'vue';
import type { Terminal, TerminalContent } from '../types';

const props = defineProps<{
  terminal: Terminal;
  content?: TerminalContent;
}>();

const emit = defineEmits<{
  'send-command': [command: string];
}>();

const terminalContentRef = ref<HTMLDivElement>();
const commandInput = ref('');
const autoScroll = ref(true);

// Send command
const sendCommand = () => {
  if (!commandInput.value.trim()) return;
  
  emit('send-command', commandInput.value);
  commandInput.value = '';
};

// Clear terminal (client-side only)
const clearTerminal = () => {
  if (terminalContentRef.value) {
    terminalContentRef.value.innerHTML = '<div class="text-gray-600 text-center mt-4">Terminal cleared (client-side only)</div>';
  }
};

// Auto-scroll to bottom when content updates
watch(() => props.content, async () => {
  if (autoScroll.value && terminalContentRef.value) {
    await nextTick();
    terminalContentRef.value.scrollTop = terminalContentRef.value.scrollHeight;
  }
});

// Keyboard shortcuts
const handleKeydown = (e: KeyboardEvent) => {
  // Ctrl+L to clear
  if (e.ctrlKey && e.key === 'l') {
    e.preventDefault();
    clearTerminal();
  }
};

onMounted(() => {
  window.addEventListener('keydown', handleKeydown);
});

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown);
});
</script>

<style scoped>
.terminal-viewer {
  /* Terminal-like styling */
}

/* Custom scrollbar for terminal */
.terminal-viewer ::-webkit-scrollbar {
  width: 8px;
}

.terminal-viewer ::-webkit-scrollbar-track {
  background: #1a1a1a;
}

.terminal-viewer ::-webkit-scrollbar-thumb {
  background: #444;
  border-radius: 4px;
}

.terminal-viewer ::-webkit-scrollbar-thumb:hover {
  background: #555;
}
</style>