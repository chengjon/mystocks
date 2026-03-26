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

  it("flags legacy guidance patterns in markdown when governance mode is enabled", () => {
    const dir = createTempDir();
    const file = join(dir, "ARTDECO_GUIDE.md");

    writeFileSync(
      file,
      `# Legacy Guide

- Font: Marcellus + Josefin Sans
- Token: var(--artdeco-accent-gold)

\`\`\`scss
@import '@/styles/artdeco-tokens.scss';

.stats-grid {
  @include artdeco-grid(4);
}
\`\`\`
`,
      "utf8",
    );

    const result = spawnSync(
      "node",
      [
        scriptPath,
        "--target-file",
        file,
        "--forbid-legacy-tokens",
        "--forbid-legacy-sass",
        "--forbid-legacy-typography",
      ],
      {
        encoding: "utf8",
        cwd: process.cwd(),
      },
    );

    expect(result.status).not.toBe(0);
    expect(result.stderr).toContain("legacy token alias");
    expect(result.stderr).toContain("legacy Sass import");
    expect(result.stderr).toContain("legacy typography reference");
    expect(result.stderr).toContain("deprecated Sass API");
  });

  it("passes governance markdown that uses current baseline terms", () => {
    const dir = createTempDir();
    const file = join(dir, "ARTDECO_GUIDE_OK.md");

    writeFileSync(
      file,
      `# Active Guide

- Font: Cinzel + Barlow + JetBrains Mono
- Token: var(--artdeco-gold-primary)

\`\`\`scss
@use '@/styles/artdeco-tokens.scss' as *;
@use '@/styles/artdeco-grid.scss' as *;

.stats-grid {
  @include artdeco-grid-4-cols;
  color: var(--artdeco-gold-primary);
}
\`\`\`
`,
      "utf8",
    );

    const result = spawnSync(
      "node",
      [
        scriptPath,
        "--target-file",
        file,
        "--forbid-legacy-tokens",
        "--forbid-legacy-sass",
        "--forbid-legacy-typography",
      ],
      {
        encoding: "utf8",
        cwd: process.cwd(),
      },
    );

    expect(result.status).toBe(0);
    expect(result.stdout).toContain("ArtDeco Token Validation Passed");
  });

  it("allows documentation literals when literal checks are explicitly skipped", () => {
    const dir = createTempDir();
    const file = join(dir, "ARTDECO_GUIDE_DOC_MODE.md");

    writeFileSync(
      file,
      `# Active Guide

- Primary gold is #D4AF37
- Recommended spacing example: 24px

\`\`\`scss
@use '@/styles/artdeco-tokens.scss' as *;

.token-sample {
  color: var(--artdeco-gold-primary);
}
\`\`\`
`,
      "utf8",
    );

    const result = spawnSync(
      "node",
      [
        scriptPath,
        "--target-file",
        file,
        "--skip-literal-checks",
        "--forbid-legacy-tokens",
        "--forbid-legacy-sass",
        "--forbid-legacy-typography",
      ],
      {
        encoding: "utf8",
        cwd: process.cwd(),
      },
    );

    expect(result.status).toBe(0);
    expect(result.stdout).toContain("ArtDeco Token Validation Passed");
  });

  it("checks only changed target files when changed-file filters are provided", () => {
    const dir = createTempDir();
    const legacyFile = join(dir, "LEGACY_GUIDE.md");
    const currentFile = join(dir, "CURRENT_GUIDE.md");

    writeFileSync(
      legacyFile,
      `# Legacy Guide

Marcellus
var(--artdeco-accent-gold)
`,
      "utf8",
    );

    writeFileSync(
      currentFile,
      `# Current Guide

Cinzel
var(--artdeco-gold-primary)
`,
      "utf8",
    );

    const result = spawnSync(
      "node",
      [
        scriptPath,
        "--target-file",
        legacyFile,
        "--target-file",
        currentFile,
        "--changed-file",
        currentFile,
        "--skip-literal-checks",
        "--forbid-legacy-tokens",
        "--forbid-legacy-typography",
      ],
      {
        encoding: "utf8",
        cwd: process.cwd(),
      },
    );

    expect(result.status).toBe(0);
    expect(result.stdout).toContain("ArtDeco Token Validation Passed");
  });

  it("still fails when the changed-file target contains legacy guidance patterns", () => {
    const dir = createTempDir();
    const legacyFile = join(dir, "LEGACY_GUIDE_CHANGED.md");

    writeFileSync(
      legacyFile,
      `# Legacy Guide

Marcellus
var(--artdeco-accent-gold)
`,
      "utf8",
    );

    const result = spawnSync(
      "node",
      [
        scriptPath,
        "--target-file",
        legacyFile,
        "--changed-file",
        legacyFile,
        "--skip-literal-checks",
        "--forbid-legacy-tokens",
        "--forbid-legacy-typography",
      ],
      {
        encoding: "utf8",
        cwd: process.cwd(),
      },
    );

    expect(result.status).not.toBe(0);
    expect(result.stderr).toContain("legacy token alias");
    expect(result.stderr).toContain("legacy typography reference");
  });
});
