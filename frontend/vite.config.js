import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/predict': 'http://127.0.0.1:5000',
      '/model-info': 'http://127.0.0.1:5000',
      '/health': 'http://127.0.0.1:5000',
      '/get_defaults': 'http://127.0.0.1:5000',
    },
  },
  build: {
    outDir: '../app/static/react',
    emptyOutDir: true,
  },
});
