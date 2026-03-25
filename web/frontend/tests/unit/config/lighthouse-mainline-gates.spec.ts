import path from "node:path";
import { describe, expect, it } from "vitest";

const frontendRoot = path.resolve(__dirname, "../../..");
const configPath = path.join(frontendRoot, "lighthouserc.cjs");

describe("Lighthouse mainline gates", () => {
  it("bootstraps authenticated collection before auditing protected routes", async () => {
    const imported = await import(configPath);
    const config = imported.default ?? imported;

    expect(config.ci.collect.puppeteerScript).toBe("./scripts/lighthouse-auth.cjs");
    expect(config.ci.collect.settings.disableStorageReset).toBe(true);
    expect(config.ci.collect.url).toEqual([
      "http://127.0.0.1:4273/login",
      "http://127.0.0.1:4273/dashboard",
      "http://127.0.0.1:4273/market/realtime",
      "http://127.0.0.1:4273/strategy/repo",
    ]);
  });
});
