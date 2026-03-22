import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

const repoRoot = resolve(process.cwd(), "..", "..");

const readFile = (relativePath: string) =>
  readFileSync(resolve(repoRoot, relativePath), "utf8");

describe("artdeco report recommendations integration", () => {
  it("keeps the current layered style imports in artdeco-main.css", () => {
    const mainCss = readFile("web/frontend/src/styles/artdeco-main.css");

    expect(mainCss).toContain("@import './artdeco-colors.css';");
    expect(mainCss).toContain("@import './artdeco-variables.css';");
    expect(mainCss).toContain("@import './artdeco-animations.css';");
  });

  it("provides the current ArtDeco variable baseline", () => {
    const variablesCss = readFile("web/frontend/src/styles/artdeco-variables.css");

    expect(variablesCss).toContain("--artdeco-bg-global:");
    expect(variablesCss).toContain("--artdeco-bg-surface:");
    expect(variablesCss).toContain("--artdeco-fg-primary:");
    expect(variablesCss).toContain("--artdeco-gold-primary:");
  });

  it("exposes the current animation baseline", () => {
    const animationsCss = readFile("web/frontend/src/styles/artdeco-animations.css");

    expect(animationsCss).toContain(".fade-enter-active");
    expect(animationsCss).toContain(".slide-up-enter-active");
    expect(animationsCss).toContain(".slide-left-enter-active");
  });
});
