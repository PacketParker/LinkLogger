import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],

  // Proxy API requests to the backend
  server: {
    proxy: {
      '/api': 'http://127.0.0.1:5252',
    },
  },
})
