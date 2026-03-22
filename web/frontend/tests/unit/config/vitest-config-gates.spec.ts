import fs from "node:fs";
import path from "node:path";
import { describe, expect, it } from "vitest";

const frontendRoot = path.resolve(__dirname, "../../..");
const vitestConfigPath = path.join(frontendRoot, "vitest.config.mts");
const vitestConfigText = fs.readFileSync(vitestConfigPath, "utf8");

describe("Vitest config gates", () => {
  it("excludes node:test style suites from the Vitest runner", () => {
    expect(vitestConfigText).toContain('"src/**/__node_tests__/**"');
  });

  it("excludes legacy src/tests suites from the main Vitest unit runner", () => {
    expect(vitestConfigText).toContain('"src/tests/**"');
  });
});
