import { defineConfig, loadEnv } from "vite"
import vue from "@vitejs/plugin-vue"
import { fileURLToPath, URL } from "node:url"

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "")
  const frontendPortRaw = env.FRONTEND_PORT || process.env.FRONTEND_PORT || process.env.PORT
  if (!frontendPortRaw) {
    throw new Error("[port-config] Missing FRONTEND_PORT in .env")
  }

  const frontendPort = Number.parseInt(frontendPortRaw, 10)
  if (!Number.isInteger(frontendPort) || frontendPort <= 0) {
    throw new Error(`[port-config] Invalid FRONTEND_PORT: ${frontendPortRaw}`)
  }

  const backendPort = env.BACKEND_PORT || process.env.BACKEND_PORT
  if (!backendPort) {
    throw new Error("[port-config] Missing BACKEND_PORT in .env")
  }

  return {
    define: {
      "import.meta.env.VITE_USE_MOCK_DATA": JSON.stringify(env.VITE_USE_MOCK_DATA === "true"),
      "import.meta.env.VITE_API_BASE_URL": JSON.stringify(env.VITE_API_BASE_URL || "/api"),
    },
    plugins: [vue()],
    resolve: {
      alias: {
        "@": fileURLToPath(new URL("../../src", import.meta.url)),
        axios: "axios/dist/browser/axios.cjs",
      },
    },
    css: {
      preprocessorOptions: {
        scss: {
          api: "modern-compiler",
          silenceDeprecations: ["legacy-js-api", "import"],
        },
      },
    },
    server: {
      host: "127.0.0.1",
      port: frontendPort,
      strictPort: true,
      proxy: {
        "/api": {
          target: `http://localhost:${backendPort}`,
          changeOrigin: true,
        },
      },
    },
  }
})
