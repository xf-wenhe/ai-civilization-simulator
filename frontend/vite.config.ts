import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 9000,  // 改为9000避免冲突
    proxy: {
      '/api': {
        target: 'http://localhost:8888',  // 后端改为8888
        changeOrigin: true
      }
    }
  }
})