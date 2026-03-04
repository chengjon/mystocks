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

const backendPort = requireEnv("BACKEND_PORT")
const backendBackupPort = requireEnv("BACKEND_BACKUP_PORT")

module.exports = {
  apps: [
    {
      name: 'mystocks-backend',
      script: 'uvicorn',
      args: `app.main:app --host 0.0.0.0 --port ${backendPort}`,
      cwd: '/opt/claude/mystocks_spec/web/backend',
      interpreter: 'python3',
      env: {
        PYTHONPATH: '/opt/claude/mystocks_spec/web/backend',
        NODE_ENV: 'development',
        BACKEND_PORT: backendPort,
        BACKEND_BACKUP_PORT: backendBackupPort,
        PORT: backendPort,
        port: backendPort,
        PORT_RANGE_END: backendBackupPort,
        port_range_end: backendBackupPort
      },
      error_file: '/root/.pm2/logs/mystocks-backend-error.log',
      out_file: '/root/.pm2/logs/mystocks-backend-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss',
      autorestart: true,
      max_restarts: 10,
      min_uptime: '10s',
      watch: false
    }
  ]
}
