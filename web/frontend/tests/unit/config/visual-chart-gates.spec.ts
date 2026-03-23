import fs from "node:fs";
import path from "node:path";
import { describe, expect, it } from "vitest";

const frontendRoot = path.resolve(__dirname, "../../..");
const packageJson = JSON.parse(
  fs.readFileSync(path.join(frontendRoot, "package.json"), "utf8"),
) as {
  scripts?: Record<string, string>;
};

const backtestSpecPath = path.join(
  frontendRoot,
  "tests/visual/components/charts/backtest.spec.ts",
);
const technicalSpecPath = path.join(
  frontendRoot,
  "tests/visual/components/charts/technical-analysis.spec.ts",
);

describe("Visual chart gates", () => {
  it("defines a dedicated chart visual smoke command", () => {
    expect(packageJson.scripts?.["test:visual:charts"]).toContain(
      "tests/visual/components/charts/backtest.spec.ts",
    );
    expect(packageJson.scripts?.["test:visual:charts"]).toContain(
      "tests/visual/components/charts/technical-analysis.spec.ts",
    );
    expect(packageJson.scripts?.["test:visual:charts:update"]).toContain("--update-snapshots");
  });

  it("keeps chart visual specs active instead of globally fixme", () => {
    const backtestSpec = fs.readFileSync(backtestSpecPath, "utf8");
    const technicalSpec = fs.readFileSync(technicalSpecPath, "utf8");

    expect(backtestSpec).not.toContain("test.describe.fixme");
    expect(technicalSpec).not.toContain("test.describe.fixme");
  });
});
