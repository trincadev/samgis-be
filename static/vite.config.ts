import {fileURLToPath, URL} from 'node:url'
import {resolve} from 'node:path'
import {defineConfig, loadEnv} from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig(({mode}) => {
    const env = loadEnv(mode, process.cwd())
    const frontendPrefix = env.VITE_INDEX_URL ? env.VITE_INDEX_URL : "/"
    console.log(`VITE_PREFIX:${env.VITE_INDEX_URL}, frontend_prefix:${frontendPrefix}, mode:${mode} ...`)
    return {
        plugins: [vue()],
        base: frontendPrefix,
        resolve: {
            alias: {
                '@': fileURLToPath(new URL('./src', import.meta.url))
            }
        },
        build: {
            rollupOptions: {
                input: {
                    index: resolve(__dirname, "index.html"),
                },
            },
        },
        test: {
            include: ['tests/**/*.{test,spec}.ts'],
            environment: 'jsdom',
            coverage: {
                provider: 'v8',
                reporter: ['text', 'html'],
                include: ['src/**/*.{ts,vue}'],
                exclude: ['src/**/*.d.ts', 'src/main.ts'],
                
                thresholds: {         
                    branches: 70,                                                                                                                                                                                                                              
                    lines: 70,          
                    functions: 70,
                    statements: 70,
                }
            },
        }
    }
})
