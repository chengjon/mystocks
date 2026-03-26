/**
 * MyStocks Frontend - PM2 Ecosystem Configuration
 * Ports are sourced from .env; hardcoded port defaults are not allowed.
 */

const fs = require("node:fs")
const path = require("node:path")

function loadEnvFile(envPath) {
  if (!fs.existsSync(envPath)) return

  const lines = fs.readFileSync(envPath, "utf8").split(/\r?\n/u)
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

for (const envPath of [path.join(__dirname, ".env"), path.join(__dirname, "..", "..", ".env")]) {
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
      name: "mystocks-frontend",
      script: "npm",
      args: `run preview -- --port ${frontendPort} --host 0.0.0.0 --strictPort`,
      cwd: "/opt/claude/mystocks_spec/web/frontend",
      env: {
        NODE_ENV: "production",
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
      max_restarts: 10,
      min_uptime: "5s",
      log_file: path.join(runtimeLogDir, "frontend-access.log"),
      error_file: path.join(runtimeLogDir, "frontend-error.log"),
      out_file: path.join(runtimeLogDir, "frontend-out.log"),
      merge_logs: true,
      exp_backoff_restart_delay: 1000
    },
    {
      name: "mystocks-frontend-static",
      script: "npm",
      args: `run preview -- --port ${frontendBackupPort} --host 0.0.0.0 --strictPort`,
      cwd: "/opt/claude/mystocks_spec/web/frontend",
      disabled: true,
      instances: 1,
      exec_mode: "fork",
      env: {
        NODE_ENV: "production",
        PORT: frontendBackupPort,
        FRONTEND_PORT: frontendBackupPort,
        BACKEND_PORT: backendPort,
        BACKEND_BACKUP_PORT: backendBackupPort,
        HOST: "0.0.0.0",
        VITE_API_BASE_URL: viteApiBaseUrl
      },
      log_file: path.join(runtimeLogDir, "frontend-static.log"),
      error_file: path.join(runtimeLogDir, "frontend-static-error.log"),
      out_file: path.join(runtimeLogDir, "frontend-static-out.log"),
      autorestart: true,
      max_restarts: 5,
      min_uptime: "30s"
    }
  ],
  deploy: {
    production: {
      user: "root",
      host: "localhost",
      ref: "origin/main",
      repo: "git@github.com:your-org/mystocks.git",
      path: "/opt/laude/mystocks_spec/web/frontend",
      "post-deploy": "npm install && npm run build && pm2 reload ecosystem.config.js --env production"
    }
  }
}
