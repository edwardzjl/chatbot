import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { viteStaticCopy } from "vite-plugin-static-copy";
import { dirname, join } from "path";
import { fileURLToPath } from "url";

// See <https://pyodide.org/en/stable/usage/working-with-bundlers.html#vite>
const PYODIDE_EXCLUDE = [
    "!**/*.{md,html}",
    "!**/*.d.ts",
    "!**/*.whl",
    "!**/node_modules",
];

export function viteStaticCopyPyodide() {
    const pyodideDir = dirname(fileURLToPath(import.meta.resolve("pyodide")));
    return viteStaticCopy({
        targets: [
            {
                src: [join(pyodideDir, "*")].concat(PYODIDE_EXCLUDE),
                dest: "assets",
            },
        ],
    });
}

// https://vite.dev/config/
export default defineConfig({
    optimizeDeps: { exclude: ["pyodide"] },
    plugins: [react(), viteStaticCopyPyodide()],
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
    },
});
