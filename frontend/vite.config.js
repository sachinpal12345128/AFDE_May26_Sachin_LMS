import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// Vite dev server runs at http://localhost:5173 by default.
// The backend FastAPI server runs at http://localhost:8000 — set via VITE_API_BASE
// (see src/api.js) or leave as the default in that file.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    open: false,
  },
});
