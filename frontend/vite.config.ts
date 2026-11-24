/// <reference types="vitest/config" />
import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig(({ mode }) => {
  const backend = loadEnv(mode, '.', 'JAPRI_').JAPRI_BACKEND_URL ?? 'http://127.0.0.1:8000'
  return {
    plugins: [react()],
    server: { proxy: { '/api': { target: backend, changeOrigin: false } } },
    test: {
      environment: 'jsdom',
      globals: true,
      setupFiles: ['./src/test-setup.ts'],
      css: false,
    },
  }
})
