import { mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { createRequire } from "node:module";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";
import { afterEach, describe, expect, it } from "vitest";

const require = createRequire(import.meta.url);
const scriptPath = resolve(process.cwd(), "scripts/check-type-error-ceiling.js");
const tempDirs: string[] = [];

const loadChecker = () => require(scriptPath);
const loadFreshChecker = () => {
  delete require.cache[scriptPath];
  return require(scriptPath);
};

const createTempDir = () => {
  const dir = mkdtempSync(join(tmpdir(), "type-ceiling-check-"));
  tempDirs.push(dir);
  return dir;
};

afterEach(() => {
  for (const dir of tempDirs.splice(0)) {
    rmSync(dir, { recursive: true, force: true });
  }
});

describe("check-type-error-ceiling", () => {
  it("defaults to a zero-error ceiling when no override is provided", () => {
    const previousCeiling = process.env.TYPE_ERROR_CEILING;
    delete process.env.TYPE_ERROR_CEILING;

    try {
      const { DEFAULT_TYPE_ERROR_CEILING } = loadFreshChecker();
      expect(DEFAULT_TYPE_ERROR_CEILING).toBe(0);
    } finally {
      if (previousCeiling === undefined) {
        delete process.env.TYPE_ERROR_CEILING;
      } else {
        process.env.TYPE_ERROR_CEILING = previousCeiling;
      }
    }
  });

  it("counts TypeScript diagnostics from vue-tsc output", () => {
    const { countTypeScriptErrors } = loadChecker();
    const output = `
src/views/Foo.vue:12:5 - error TS2322: Type 'string' is not assignable to type 'number'.
src/api/bar.ts:4:9 - error TS2304: Cannot find name 'window'.
`;

    expect(countTypeScriptErrors(output)).toBe(2);
  });

  it("evaluates the current ceiling without mutating the long-term baseline", () => {
    const { evaluateTypeErrorCeiling } = loadChecker();
    const output = `
src/views/Foo.vue:12:5 - error TS2322: Type 'string' is not assignable to type 'number'.
src/api/bar.ts:4:9 - error TS2304: Cannot find name 'window'.
`;

    expect(evaluateTypeErrorCeiling({ output, ceiling: 2 })).toEqual({
      ceiling: 2,
      errorCount: 2,
      ok: true,
    });

    expect(evaluateTypeErrorCeiling({ output, ceiling: 1 })).toEqual({
      ceiling: 1,
      errorCount: 2,
      ok: false,
    });
  });

  it("loads diagnostics from an existing type-check output file", () => {
    const { readTypeCheckOutput } = loadChecker();
    const dir = createTempDir();
    const outputFile = join(dir, "vue-tsc-output.txt");

    writeFileSync(
      outputFile,
      "src/views/Foo.vue:12:5 - error TS2322: Type 'string' is not assignable to type 'number'.\n",
      "utf8",
    );

    expect(readTypeCheckOutput({ inputFile: outputFile })).toContain("error TS2322");
  });
});
