import * as fs from "node:fs"
import * as path from "node:path"

import { defineConfig } from "@playwright/test"

function loadEnvFile(envPath: string): void {
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

const cwd = process.cwd()
loadEnvFile(path.join(cwd, ".env"))
loadEnvFile(path.join(cwd, "..", "..", ".env"))

const frontendPortRaw = process.env.FRONTEND_PORT
if (!frontendPortRaw) {
  throw new Error("[port-config] Missing FRONTEND_PORT in .env")
}

const frontendPort = Number.parseInt(frontendPortRaw, 10)
if (!Number.isInteger(frontendPort) || frontendPort <= 0) {
  throw new Error(`[port-config] Invalid FRONTEND_PORT: ${frontendPortRaw}`)
}

export default defineConfig({
  testDir: "./tests",
  testMatch: "**/*.spec.ts",
  timeout: 60000,
  use: {
    headless: true,
    ignoreHTTPSErrors: true,
    baseURL: `http://localhost:${frontendPort}`,
  },
  projects: [
    {
      name: "chromium",
      use: { browserName: "chromium" },
    },
  ],
})
