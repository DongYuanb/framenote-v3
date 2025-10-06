import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";
import path from "path";
import { componentTagger } from "lovable-tagger";

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => ({
  server: {
    host: "::",
    port: 8080,
    // ✅ 允许 Cloudflare Tunnel 访问
    allowedHosts: [
      "ab-olympic-sponsored-proudly.trycloudflare.com"
    ],
    proxy: {
      "/api": { target: "http://localhost:8001", changeOrigin: true },
      "/storage": { target: "http://localhost:8001", changeOrigin: true }
    }
  },
  plugins: [
    react(),
    mode === 'development' && componentTagger(),
  ].filter(Boolean),
  resolve: {
    alias: { "@": path.resolve(__dirname, "./src") },
  },
}));