import fs from "node:fs";
import path from "node:path";
import { describe, expect, it } from "vitest";

const frontendRoot = path.resolve(__dirname, "../../..");
const vitestConfigPath = path.join(frontendRoot, "vitest.config.mts");
const packageJsonPath = path.join(frontendRoot, "package.json");

const vitestConfigText = fs.readFileSync(vitestConfigPath, "utf8");
const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, "utf8")) as {
  devDependencies?: Record<string, string>;
};

describe("Vitest MSW gates", () => {
  it("loads a shared vitest setup file for test infrastructure", () => {
    expect(vitestConfigText).toContain('setupFiles: ["./vitest.setup.ts"]');
  });

  it("declares msw as a direct dev dependency", () => {
    expect(packageJson.devDependencies?.msw).toBeDefined();
  });
});
