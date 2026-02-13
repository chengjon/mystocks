import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

const repoRoot = resolve(process.cwd(), "..", "..");

const readFile = (relativePath: string) =>
  readFileSync(resolve(repoRoot, relativePath), "utf8");

describe("artdeco governance cli", () => {
  it("exposes strict governance check script", () => {
    const packageJson = JSON.parse(readFile("web/frontend/package.json"));

    expect(packageJson.scripts["lint:artdeco:strict"]).toBeTruthy();
  });

  it("documents governance verification commands and report linkage", () => {
    const guideText = readFile("docs/guides/ARTDECO_COMPONENT_GUIDE.md");
    const indexText = readFile("docs/guides/ARTDECO_MASTER_INDEX.md");

    expect(guideText).toContain("lint:artdeco:strict");
    expect(guideText).toContain("prefers-reduced-motion");
    expect(indexText).toContain(
      "ARTDECO_UI_UX_OPTIMIZATION_RECOMMENDATIONS.md",
    );
  });
});
