const fs = require("node:fs");
const path = require("node:path");

function loadEnvFile(envPath) {
  if (!fs.existsSync(envPath)) {
    return;
  }

  const lines = fs.readFileSync(envPath, "utf8").split(/\r?\n/u);
  for (const line of lines) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith("#")) {
      continue;
    }

    const separatorIndex = trimmed.indexOf("=");
    if (separatorIndex <= 0) {
      continue;
    }

    const key = trimmed.slice(0, separatorIndex).trim();
    if (!key || process.env[key] !== undefined) {
      continue;
    }

    let value = trimmed.slice(separatorIndex + 1).trim();
    if (
      (value.startsWith("\"") && value.endsWith("\"")) ||
      (value.startsWith("'") && value.endsWith("'"))
    ) {
      value = value.slice(1, -1);
    }
    process.env[key] = value;
  }
}

if (typeof process.loadEnvFile === "function") {
  for (const envFile of [path.join(__dirname, ".env"), path.join(__dirname, "web", "frontend", ".env")]) {
    if (fs.existsSync(envFile)) {
      process.loadEnvFile(envFile);
    }
  }
} else {
  for (const envFile of [path.join(__dirname, ".env"), path.join(__dirname, "web", "frontend", ".env")]) {
    loadEnvFile(envFile);
  }
}

function requireEnv(name) {
  const value = process.env[name];
  if (!value) {
    throw new Error(`[port-config] Missing required env var: ${name}`);
  }
  return value;
}

const backendPort = requireEnv("BACKEND_PORT");
const backendBackupPort = requireEnv("BACKEND_BACKUP_PORT");
const frontendPort = requireEnv("FRONTEND_PORT");
const frontendBackupPort = requireEnv("FRONTEND_BACKUP_PORT");
const viteApiBaseUrl = process.env.VITE_API_BASE_URL || `http://localhost:${backendPort}`;
const viteWsUrl = process.env.VITE_WS_URL || `ws://localhost:${backendPort}`;

module.exports = {
  apps: [
    {
      name: 'mystocks-backend',
      script: 'python3',
      args: `-m uvicorn app.main:app --host 0.0.0.0 --port ${backendPort}`,
      cwd: './web/backend',
      min_uptime: '10s',
      restart_delay: 5000,
      max_restarts: 10,
      env: {
        PYTHONPATH: '/opt/claude/mystocks_spec/web/backend', 
        VITE_APP_MODE: 'mock',
        PORT: backendPort,
        BACKEND_PORT: backendPort,
        BACKEND_BACKUP_PORT: backendBackupPort,
        port: backendPort,
        port_range_end: backendBackupPort
      }
    },
    {
      name: 'mystocks-frontend',
      script: 'npm',
      args: `run dev -- --port ${frontendPort} --host 0.0.0.0 --strictPort`,
      cwd: './web/frontend',
      env: {
        FRONTEND_PORT: frontendPort,
        FRONTEND_BACKUP_PORT: frontendBackupPort,
        BACKEND_PORT: backendPort,
        BACKEND_BACKUP_PORT: backendBackupPort,
        VITE_API_BASE_URL: viteApiBaseUrl,
        VITE_WS_URL: viteWsUrl,
        VITE_PORT: frontendPort, 
        PORT: frontendPort
      }
    }
  ]
};
