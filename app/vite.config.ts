import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],

  // Proxy to the backend server
  server: {
    proxy: {
      '/api': 'http://localhost:5252',
    },
  },
})
