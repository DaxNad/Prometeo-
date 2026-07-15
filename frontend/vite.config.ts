import { defineConfig, loadEnv, type ProxyOptions } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");
  const apiKey =
    process.env.PROMETEO_API_KEY ||
    env.PROMETEO_API_KEY ||
    env.VITE_PROMETEO_API_KEY ||
    "";

  const proxyTarget: ProxyOptions = {
    target: "http://127.0.0.1:8000",
    changeOrigin: true,
    configure: (proxy) => {
      proxy.on("proxyReq", (proxyReq) => {
        if (!apiKey) return;
        proxyReq.setHeader("x-api-key", apiKey);
      });
    }
  };

  return {
    plugins: [react()],
    server: {
      port: 5173,
      strictPort: true,
      proxy: {
        "/production": proxyTarget,
        "/health": proxyTarget,
        "/agent-runtime": proxyTarget,
        "/tl/chat": proxyTarget
      }
    }
  };
});
