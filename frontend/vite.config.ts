import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 3000,
    proxy: {
      '/api/v2': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
        ws: true,
      },
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
      },
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          // Group features by domain for better caching
          communication: ['./src/pages/ChatPage.tsx', './src/features/chat'],
          knowledge: [
            './src/pages/Knowledge.tsx',
            './src/pages/NotesPage.tsx',
            './src/features/notes',
          ],
          productivity: ['./src/pages/TasksPage.tsx', './src/features/tasks'],
          automation: ['./src/pages/AgentsPage.tsx', './src/features/agents'],
          creative: ['./src/pages/CanvasPage.tsx', './src/features/canvas'],
          vendor: ['react', 'react-dom', 'antd'],
        },
      },
    },
  },
});
