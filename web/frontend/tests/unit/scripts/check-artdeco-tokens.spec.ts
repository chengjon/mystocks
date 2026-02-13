import { mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { join, resolve } from "node:path";
import { tmpdir } from "node:os";
import { spawnSync } from "node:child_process";
import { afterEach, describe, expect, it } from "vitest";

const scriptPath = resolve(process.cwd(), "scripts/check-artdeco-tokens.js");

const tempDirs: string[] = [];

const createTempDir = () => {
  const dir = mkdtempSync(join(tmpdir(), "artdeco-token-check-"));
  tempDirs.push(dir);
  return dir;
};

const runChecker = (targetDir: string) =>
  spawnSync("node", [scriptPath, "--strict", "--target-dir", targetDir], {
    encoding: "utf8",
    cwd: process.cwd(),
  });

afterEach(() => {
  for (const dir of tempDirs.splice(0)) {
    rmSync(dir, { recursive: true, force: true });
  }
});

describe("check-artdeco-tokens", () => {
  it("flags duplicate custom properties and ignores non-style blocks", () => {
    const dir = createTempDir();
    const file = join(dir, "DuplicateVar.vue");

    writeFileSync(
      file,
      `<template><div>#FF0000 in template should be ignored</div></template>
<script setup lang="ts">
const scriptValue = "#00FF00";
</script>
<style scoped lang="scss">
.panel {
  --artdeco-panel-color: var(--artdeco-bg-card);
  --artdeco-panel-color: var(--artdeco-bg-base);
}
</style>`,
      "utf8",
    );

    const result = runChecker(dir);

    expect(result.status).not.toBe(0);
    expect(result.stderr).toContain("duplicate custom property");
    expect(result.stderr).not.toContain("template should be ignored");
  });

  it("passes when hardcoded literals only appear outside style", () => {
    const dir = createTempDir();
    const file = join(dir, "NonStyleLiteral.vue");

    writeFileSync(
      file,
      `<template><div>#FFFFFF outside style block</div></template>
<script setup lang="ts">
const cssLike = "padding: 24px";
</script>
<style scoped lang="scss">
.ok {
  color: var(--artdeco-fg-primary);
  margin: var(--artdeco-spacing-4);
  border-width: 1px;
}
</style>`,
      "utf8",
    );

    const result = runChecker(dir);

    expect(result.status).toBe(0);
    expect(result.stdout).toContain("ArtDeco Token Validation Passed");
  });
});
