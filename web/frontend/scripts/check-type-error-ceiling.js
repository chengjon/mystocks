#!/usr/bin/env node

const { spawnSync } = require("node:child_process");
const fs = require("node:fs");

const DEFAULT_TYPE_ERROR_CEILING = Number.parseInt(process.env.TYPE_ERROR_CEILING || "0", 10);

function countTypeScriptErrors(output) {
  return Array.from(output.matchAll(/\berror TS\d+:/gu)).length;
}

function evaluateTypeErrorCeiling({ output, ceiling }) {
  const errorCount = countTypeScriptErrors(output);

  return {
    ceiling,
    errorCount,
    ok: errorCount <= ceiling,
  };
}

function readTypeCheckOutput({ inputFile } = {}) {
  if (!inputFile) {
    return null;
  }

  return fs.readFileSync(inputFile, "utf8");
}

function runTypeCheckGate({ cwd = process.cwd(), ceiling = DEFAULT_TYPE_ERROR_CEILING, inputFile } = {}) {
  const fileOutput = readTypeCheckOutput({ inputFile });

  if (fileOutput !== null) {
    const summary = evaluateTypeErrorCeiling({
      output: fileOutput,
      ceiling,
    });

    return {
      ...summary,
      spawnError: null,
      status: 0,
      stdout: "",
      stderr: "",
      source: "file",
    };
  }

  const result = spawnSync("npm", ["run", "type-check"], {
    cwd,
    encoding: "utf8",
    shell: process.platform === "win32",
  });

  const stdout = result.stdout || "";
  const stderr = result.stderr || "";
  const summary = evaluateTypeErrorCeiling({
    output: `${stdout}\n${stderr}`,
    ceiling,
  });

  return {
    ...summary,
    spawnError: result.error || null,
    status: typeof result.status === "number" ? result.status : 1,
    stdout,
    stderr,
    source: "command",
  };
}

function parseArgs(argv) {
  const options = {
    inputFile: undefined,
  };

  for (let index = 0; index < argv.length; index += 1) {
    const value = argv[index];

    if (value === "--input-file") {
      options.inputFile = argv[index + 1];
      index += 1;
    }
  }

  return options;
}

if (require.main === module) {
  const args = parseArgs(process.argv.slice(2));
  const gateResult = runTypeCheckGate({ inputFile: args.inputFile });

  if (gateResult.stdout) {
    process.stdout.write(gateResult.stdout);
  }

  if (gateResult.stderr) {
    process.stderr.write(gateResult.stderr);
  }

  if (gateResult.spawnError) {
    console.error(`[type-ceiling] Failed to execute type-check: ${gateResult.spawnError.message}`);
    process.exit(1);
  }

  if (gateResult.status !== 0 && gateResult.errorCount === 0) {
    console.error("[type-ceiling] type-check exited non-zero without TypeScript diagnostics; treating this as an execution failure.");
    process.exit(gateResult.status || 1);
  }

  if (!gateResult.ok) {
    console.error(
      `[type-ceiling] TypeScript errors ${gateResult.errorCount} exceed configured ceiling ${gateResult.ceiling}.`,
    );
    process.exit(1);
  }

  console.log(`[type-ceiling] TypeScript errors ${gateResult.errorCount} are within configured ceiling ${gateResult.ceiling}.`);
}

module.exports = {
  DEFAULT_TYPE_ERROR_CEILING,
  countTypeScriptErrors,
  evaluateTypeErrorCeiling,
  parseArgs,
  readTypeCheckOutput,
  runTypeCheckGate,
};
