import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Local dev: proxy API paths to Lab 2 microservices (same routing idea as frontend/nginx.conf).
const proxyTo = {
  '^/auth/user': 'http://127.0.0.1:8001',
  '^/auth/owner': 'http://127.0.0.1:8002',
  '^/auth': 'http://127.0.0.1:8001',
  '^/users': 'http://127.0.0.1:8001',
  '^/owner': 'http://127.0.0.1:8002',
  '^/restaurants/\\d+/reviews': 'http://127.0.0.1:8004',
  '^/restaurants': 'http://127.0.0.1:8003',
  '^/reviews': 'http://127.0.0.1:8004',
  '^/events': 'http://127.0.0.1:8004',
  '^/ai-assistant': 'http://127.0.0.1:8003',
  '^/uploads': 'http://127.0.0.1:8003',
}

const proxy = Object.fromEntries(
  Object.entries(proxyTo).map(([path, target]) => [
    path,
    { target, changeOrigin: true },
  ])
)

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy,
  },
})
