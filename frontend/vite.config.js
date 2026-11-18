import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// In development the dashboard calls /api/..., which Vite forwards to the
// alert service. In the container, Nginx does the same (see nginx.conf),
// so the built app never needs to know a service address.
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: process.env.ALERT_SERVICE_URL || 'http://127.0.0.1:8003',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
})
