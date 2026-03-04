const fs = require("node:fs")
const path = require("node:path")

function parseAndLoadEnvFallback(envPath) {
  if (!fs.existsSync(envPath)) {
    return
  }

  const lines = fs.readFileSync(envPath, "utf8").split(/\r?\n/u)
  for (const line of lines) {
    const trimmed = line.trim()
    if (!trimmed || trimmed.startsWith("#")) {
      continue
    }

    const separatorIndex = trimmed.indexOf("=")
    if (separatorIndex <= 0) {
      continue
    }

    const key = trimmed.slice(0, separatorIndex).trim()
    if (!key || process.env[key] !== undefined) {
      continue
    }

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

function loadPortEnv(baseDir = process.cwd()) {
  const envPaths = [path.join(baseDir, ".env"), path.join(baseDir, "..", "..", ".env")]

  for (const envPath of envPaths) {
    if (typeof process.loadEnvFile === "function") {
      try {
        process.loadEnvFile(envPath)
        continue
      } catch {
        // Fall back for Node versions without a working loadEnvFile.
      }
    }
    parseAndLoadEnvFallback(envPath)
  }
}

function readPort(...envKeys) {
  for (const key of envKeys) {
    const value = process.env[key]
    if (!value) {
      continue
    }

    const port = Number.parseInt(value, 10)
    if (Number.isInteger(port) && port > 0) {
      return port
    }
  }
  return null
}

function requirePort(port, label) {
  if (!port) {
    throw new Error(`[port-config] Missing or invalid ${label} in .env`)
  }
  return port
}

function resolveFrontendConfig() {
  const port = requirePort(
    readPort("E2E_FRONTEND_PORT", "FRONTEND_PORT", "VITE_PORT", "PORT", "FRONTEND_PORT_RANGE_START"),
    "FRONTEND_PORT"
  )
  const backupPort = requirePort(readPort("FRONTEND_BACKUP_PORT"), "FRONTEND_BACKUP_PORT")
  const baseUrl = process.env.E2E_FRONTEND_URL || process.env.FRONTEND_BASE_URL || `http://localhost:${port}`
  return { port, backupPort, baseUrl }
}

function resolveBackendConfig() {
  const port = requirePort(readPort("E2E_BACKEND_PORT", "BACKEND_PORT", "BACKEND_PORT_RANGE_START"), "BACKEND_PORT")
  const backupPort = requirePort(readPort("BACKEND_BACKUP_PORT"), "BACKEND_BACKUP_PORT")
  const baseUrl = process.env.E2E_BACKEND_URL || process.env.BACKEND_BASE_URL || `http://localhost:${port}`
  return { port, backupPort, baseUrl }
}

module.exports = {
  loadPortEnv,
  readPort,
  resolveFrontendConfig,
  resolveBackendConfig
}
