import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";
import path from "path";
import { componentTagger } from "lovable-tagger";

// https://vitejs.dev/config/


export default defineConfig({
  plugins: [react()],
  root: '.', // Use current directory as root
  base: '/', // Important for Django static files
  build: {
    outDir: '../backend/static/frontend', // Output to Django static dir
    emptyOutDir: true,
    manifest: true, // Required by django-vite
    rollupOptions: {
      input: '/src/main.jsx' // or your entry file
    }
  },
  server: {
    port: 5173,
    strictPort: true,
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'), // Optional: Use `@/` to reference `src/`
    },
  },
})


// export default defineConfig(({ mode }) => ({
//   server: {
//     host: "::",
//     port: 8080,
//   },
//   plugins: [
//     react(),
//     mode === 'development' &&
//     componentTagger(),
//   ].filter(Boolean),
//   resolve: {
//     alias: {
//       "@": path.resolve(__dirname, "./src"),
//     },
//   },
// }));
