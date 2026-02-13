import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

const repoRoot = resolve(process.cwd(), "..", "..");

const readFile = (relativePath: string) =>
  readFileSync(resolve(repoRoot, relativePath), "utf8");

describe("artdeco report recommendations integration", () => {
  it("removes conflicting colors import from artdeco-main.css", () => {
    const mainCss = readFile("web/frontend/src/styles/artdeco-main.css");

    expect(mainCss).not.toContain("@import './artdeco-colors.css';");
  });

  it("provides compatibility aliases and trust-blue token", () => {
    const variablesCss = readFile("web/frontend/src/styles/artdeco-variables.css");

    expect(variablesCss).toContain("--artdeco-bg-primary:");
    expect(variablesCss).toContain("--artdeco-bg-secondary:");
    expect(variablesCss).toContain("--artdeco-text-primary:");
    expect(variablesCss).toContain("--artdeco-trust-blue:");
  });

  it("exposes reduced-motion fallback in animation baseline", () => {
    const animationsCss = readFile("web/frontend/src/styles/artdeco-animations.css");

    expect(animationsCss).toContain("@media (prefers-reduced-motion: reduce)");
  });
});
