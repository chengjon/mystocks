const fs = require("node:fs")
const path = require("node:path")

function loadEnvFile(envPath) {
  if (!fs.existsSync(envPath)) return

  let lines
  try {
    lines = fs.readFileSync(envPath, "utf8").split(/\r?\n/u)
  } catch {
    return
  }
  for (const line of lines) {
    const trimmed = line.trim()
    if (!trimmed || trimmed.startsWith("#")) continue
    const separatorIndex = trimmed.indexOf("=")
    if (separatorIndex <= 0) continue
    const key = trimmed.slice(0, separatorIndex).trim()
    if (!key || process.env[key] !== undefined) continue

    let value = trimmed.slice(separatorIndex + 1).trim()
    if (
      (value.startsWith('"') && value.endsWith('"')) ||
      (value.startsWith("'") && value.endsWith("'"))
    ) {
      value = value.slice(1, -1)
    }
    process.env[key] = value
  }
}

for (const envPath of [path.join(__dirname, ".env"), path.join(__dirname, "..", ".env")]) {
  if (typeof process.loadEnvFile === "function") {
    try {
      process.loadEnvFile(envPath)
      continue
    } catch {
      // fall through to manual parser
    }
  }
  loadEnvFile(envPath)
}

function requireEnv(name) {
  const value = process.env[name]
  if (!value) {
    throw new Error(`[port-config] Missing required env var: ${name}`)
  }
  return value
}

const frontendPort = requireEnv("FRONTEND_PORT")
const frontendBackupPort = requireEnv("FRONTEND_BACKUP_PORT")
const backendPort = requireEnv("BACKEND_PORT")
const backendBackupPort = requireEnv("BACKEND_BACKUP_PORT")
const viteApiBaseUrl = process.env.VITE_API_BASE_URL || `http://localhost:${backendPort}`
const runtimeLogDir = "/opt/claude/mystocks_spec/var/log"

fs.mkdirSync(runtimeLogDir, { recursive: true })

module.exports = {
  apps: [
    {
      name: "mystocks-frontend-dev",
      script: "npm",
      args: "run dev -- --host 0.0.0.0 --strictPort",
      cwd: "/opt/claude/mystocks_spec/web/frontend",
      env: {
        NODE_ENV: "development",
        PORT: frontendPort,
        FRONTEND_PORT: frontendPort,
        FRONTEND_BACKUP_PORT: frontendBackupPort,
        BACKEND_PORT: backendPort,
        BACKEND_BACKUP_PORT: backendBackupPort,
        HOST: "0.0.0.0",
        VITE_API_BASE_URL: viteApiBaseUrl
      },
      instances: 1,
      exec_mode: "fork",
      autorestart: true,
      watch: false,
      ignore_watch: ["node_modules", "dist", ".git"],
      max_memory_restart: "1G",
      error_file: path.join(runtimeLogDir, "frontend-dev-error.log"),
      out_file: path.join(runtimeLogDir, "frontend-dev-out.log"),
      log_date_format: "YYYY-MM-DD HH:mm:ss Z",
      merge_logs: true,
      min_uptime: "5s",
      max_restarts: 10,
      restart_delay: 2000,
      kill_timeout: 5000,
      listen_timeout: 10000,
      node_args: "--max-old-space-size=1024"
    },
    {
      name: "mystocks-backend",
      script: "python",
      args: "pm2_start.py",
      cwd: "/opt/claude/mystocks_spec/web/backend",
      env: {
        TESTING: "false",
        USE_MOCK_DATA: "false",
        BACKEND_PORT: backendPort,
        BACKEND_BACKUP_PORT: backendBackupPort,
        REDIS_HOST: "localhost",
        REDIS_PORT: "6379"
      },
      instances: 1,
      exec_mode: "fork",
      autorestart: true,
      max_memory_restart: "1G",
      error_file: path.join(runtimeLogDir, "backend-error.log"),
      out_file: path.join(runtimeLogDir, "backend-out.log"),
      log_date_format: "YYYY-MM-DD HH:mm:ss Z",
      merge_logs: true,
      min_uptime: "10s",
      max_restarts: 10,
      restart_delay: 3000,
      kill_timeout: 10000,
      listen_timeout: 15000
    }
  ]
}
