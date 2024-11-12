import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],

  // Run on 127.0.0.1
  server: {
    host: '127.0.0.1',
    proxy: {
      '/api': 'http://127.0.0.1:5252',
    },
  },
})
