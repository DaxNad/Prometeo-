import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

const apiKey = process.env.PROMETEO_API_KEY || "";

const proxyTarget = {
  target: "http://127.0.0.1:8000",
  changeOrigin: true,
  headers: apiKey ? { "X-API-Key": apiKey } : {}
};

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    strictPort: true,
    proxy: {
      "/production": proxyTarget,
      "/health": proxyTarget,
      "/agent-runtime": proxyTarget,
      "/tl": proxyTarget
    }
  }
});
