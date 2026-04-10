import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api': 'http://localhost:10000',
      '/auth': 'http://localhost:10000',
      '/chat': 'http://localhost:10000',
      '/admin': 'http://localhost:10000',
      '/upload': 'http://localhost:10000'
    }
  }
})
