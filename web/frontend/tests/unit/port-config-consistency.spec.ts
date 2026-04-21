import fs from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";
import { describe, expect, it } from "vitest";

const require = createRequire(import.meta.url);
const frontendRoot = path.resolve(__dirname, "../..");
const repoRoot = path.resolve(frontendRoot, "..", "..");

describe("Port configuration consistency", () => {
  it("pins Vite dev server port and enables strictPort", () => {
    const viteConfigPath = path.join(frontendRoot, "vite.config.mts");
    const viteConfigText = fs.readFileSync(viteConfigPath, "utf8");

    expect(viteConfigText).toMatch(/port:\s*devPort/);
    expect(viteConfigText).toMatch(/strictPort:\s*true/);
  });

  it("pins frontend PM2 dev server to 3020 with strictPort", () => {
    const pm2ConfigPath = path.join(frontendRoot, "ecosystem.config.js");
    const pm2Config = require(pm2ConfigPath);
    const frontendApp = pm2Config.apps.find((app: { name: string }) => app.name === "mystocks-frontend");

    expect(frontendApp).toBeDefined();
    expect(frontendApp.args).toContain("--port 3020");
    expect(frontendApp.args).toContain("--strictPort");
  });

  it("pins test PM2 frontend server to 3020", () => {
    const testPm2ConfigPath = path.join(repoRoot, "ecosystem.test.config.js");
    const testPm2Config = require(testPm2ConfigPath);
    const frontendApp = testPm2Config.apps.find((app: { name: string }) => app.name === "mystocks-frontend");

    expect(frontendApp).toBeDefined();
    expect(frontendApp.args).toContain("--port 3020");
    expect(Number(frontendApp.env.PORT)).toBe(3020);
  });

  it("uses 3020 as default e2e base URL", () => {
    const playwrightConfigPath = path.join(frontendRoot, "playwright.config.js");
    const portHelperPath = path.join(frontendRoot, "tests/e2e/helpers/port-env.js");

    const playwrightConfigText = fs.readFileSync(playwrightConfigPath, "utf8");
    const { loadPortEnv, resolveFrontendConfig } = require(portHelperPath);

    loadPortEnv(frontendRoot);

    expect(resolveFrontendConfig().port).toBe(3020);
    expect(resolveFrontendConfig().baseUrl).toBe("http://localhost:3020");
    expect(playwrightConfigText).toContain("const baseURL = process.env.FRONTEND_BASE_URL || resolvedFrontend.baseUrl;");
    expect(fs.existsSync(path.join(frontendRoot, "cypress.config.ts"))).toBe(false);
  });
});
