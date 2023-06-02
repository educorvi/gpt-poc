import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue({
      template: {
        compilerOptions: {
          isCustomElement: (tag) => tag.includes('simple-websocket-chat')
        }
      },
      customElement: true
    })],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  define: { 'process.env.NODE_ENV': '"production"' },
  build: {
    outDir: 'webcomponent_dist',
    lib: {
      entry: './src/webcomponent.ce.ts',
      name: 'simple-websocket-chat',
      // the proper extensions will be added
      fileName: 'simple-websocket-chat',
      formats: ["es", "umd", "cjs"]
    },

  },
})
