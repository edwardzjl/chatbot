import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { compression } from 'vite-plugin-compression2'

// https://vite.dev/config/
export default defineConfig({
    plugins: [react(), compression({algorithm: 'brotliCompress'})],
    server: {
        port: '3000',
        proxy: {
            '/metrics': {
                target: 'http://127.0.0.1:8000',
                changeOrigin: true,
            },
            '/api': {
                target: 'http://127.0.0.1:8000',
                changeOrigin: true,
                headers: {
                    'X-Forwarded-User': 'dev',
                    'X-Forwarded-Preferred-Username': 'dev',
                    'X-Forwarded-Email': 'dev@jlzhou.me',
                },
                ws: true,
            },
        },
    },
    resolve: {
        alias: {
            '@/': '/src/',
            'micromark-extension-math': 'micromark-extension-llm-math',
        },
        conditions: ['mui-modern', 'module', 'browser', 'development|production']
    },
})
