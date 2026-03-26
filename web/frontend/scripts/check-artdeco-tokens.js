const fs = require("fs");
const path = require("path");
const { spawnSync } = require("node:child_process");

const COLOR_LITERAL_REGEX = /#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})\b|rgb\s*\(|hsl\s*\(/;
const PX_LITERAL_REGEX = /\b\d+px\b/;
const DUPLICATE_PROP_REGEX = /^\s*(--artdeco-[a-zA-Z0-9-]+)\s*:/;
const LEGACY_TOKEN_PATTERNS = [
  /--artdeco-accent-gold\b/,
  /--artdeco-color-up\b/,
  /--artdeco-color-down\b/,
  /--artdeco-color-flat\b/,
  /--artdeco-fall\b/,
];
const LEGACY_SASS_IMPORT_REGEX = /@import\s+['"][^'"]*artdeco-(?:tokens|grid|patterns|financial|quant-extended)(?:\.scss)?['"]/;
const DEPRECATED_SASS_API_PATTERNS = [
  /@include\s+artdeco-grid\s*\(/,
  /@include\s+artdeco-glow\s*\(/,
  /@include\s+artdeco-section-divider\s*\(/,
];
const LEGACY_TYPOGRAPHY_PATTERNS = [/\bMarcellus\b/, /\bJosefin Sans\b/];

function stripComments(content) {
  return content
    .replace(/\/\*[\s\S]*?\*\//g, "")
    .split("\n")
    .filter((line) => !line.trim().startsWith("//"))
    .join("\n");
}

function extractStyleBlocks(content, filePath) {
  if (!filePath.endsWith(".vue")) {
    return [content];
  }

  const matches = [];
  const regex = /<style\b[^>]*>([\s\S]*?)<\/style>/gi;
  let match = regex.exec(content);
  while (match) {
    matches.push(match[1]);
    match = regex.exec(content);
  }
  return matches;
}

function analyzeContent(content, options) {
  const checkLiterals = options?.checkLiterals !== false;
  const strict = Boolean(options?.strict);
  const forbidLegacyTokens = Boolean(options?.forbidLegacyTokens);
  const forbidLegacySass = Boolean(options?.forbidLegacySass);
  const forbidLegacyTypography = Boolean(options?.forbidLegacyTypography);
  const literalAllowList = options?.literalAllowList ?? ["0px", "1px"];
  const filePath = options?.filePath ?? "unknown";

  const cleaned = stripComments(content);
  const lines = cleaned.split("\n");
  const errors = [];
  const customPropertyLines = new Map();

  lines.forEach((line, index) => {
    const lineNumber = index + 1;
    const trimmed = line.trim();
    if (!trimmed) {
      return;
    }

    if (checkLiterals) {
      if (COLOR_LITERAL_REGEX.test(trimmed)) {
        errors.push(
          `${filePath}:${lineNumber}: hardcoded color literal found; use var(--artdeco-*)`,
        );
      }

      const pxMatches = trimmed.match(PX_LITERAL_REGEX) ?? [];
      for (const match of pxMatches) {
        if (!literalAllowList.includes(match)) {
          errors.push(
            `${filePath}:${lineNumber}: hardcoded spacing literal (${match}) found; use ArtDeco spacing tokens`,
          );
        }
      }
    }

    if (strict) {
      const duplicateMatch = trimmed.match(DUPLICATE_PROP_REGEX);
      if (duplicateMatch) {
        const propertyName = duplicateMatch[1];
        if (customPropertyLines.has(propertyName)) {
          const firstLine = customPropertyLines.get(propertyName);
          errors.push(
            `${filePath}:${lineNumber}: duplicate custom property "${propertyName}" (first defined at line ${firstLine})`,
          );
        } else {
          customPropertyLines.set(propertyName, lineNumber);
        }
      }
    }

    if (forbidLegacyTokens) {
      for (const pattern of LEGACY_TOKEN_PATTERNS) {
        if (pattern.test(trimmed)) {
          errors.push(
            `${filePath}:${lineNumber}: legacy token alias found; use active ArtDeco baseline tokens`,
          );
          break;
        }
      }
    }

    if (forbidLegacySass) {
      if (LEGACY_SASS_IMPORT_REGEX.test(trimmed)) {
        errors.push(
          `${filePath}:${lineNumber}: legacy Sass import found; prefer @use for ArtDeco style modules`,
        );
      }

      for (const pattern of DEPRECATED_SASS_API_PATTERNS) {
        if (pattern.test(trimmed)) {
          errors.push(
            `${filePath}:${lineNumber}: deprecated Sass API found; use active ArtDeco mixins/classes from the baseline`,
          );
          break;
        }
      }
    }

    if (forbidLegacyTypography) {
      for (const pattern of LEGACY_TYPOGRAPHY_PATTERNS) {
        if (pattern.test(trimmed)) {
          errors.push(
            `${filePath}:${lineNumber}: legacy typography reference found; use the active ArtDeco font stack`,
          );
          break;
        }
      }
    }
  });

  return { errors };
}

function listTargetFiles(targetDir) {
  const results = [];

  const walk = (dirPath) => {
    if (!fs.existsSync(dirPath)) {
      return;
    }

    const entries = fs.readdirSync(dirPath, { withFileTypes: true });
    for (const entry of entries) {
      const fullPath = path.join(dirPath, entry.name);
      if (entry.isDirectory()) {
        walk(fullPath);
        continue;
      }

      if (/\.(vue|scss|css|md)$/.test(entry.name)) {
        results.push(fullPath);
      }
    }
  };

  walk(targetDir);
  return results;
}

function resolveTargetFiles({
  targetDir,
  targetFiles = [],
  includeTargetDir = false,
  changedFiles = [],
}) {
  const resolved = new Set();
  const shouldIncludeTargetDir = targetFiles.length === 0 || includeTargetDir;

  for (const filePath of targetFiles) {
    if (fs.existsSync(filePath) && fs.statSync(filePath).isFile()) {
      resolved.add(filePath);
    }
  }

  if (shouldIncludeTargetDir) {
    for (const filePath of listTargetFiles(targetDir)) {
      resolved.add(filePath);
    }
  }

  if (changedFiles.length === 0) {
    return [...resolved];
  }

  const changedSet = new Set(changedFiles.map((filePath) => path.resolve(filePath)));
  return [...resolved].filter((filePath) => changedSet.has(path.resolve(filePath)));
}

function resolveGitChangedFiles({ cwd = process.cwd(), baseRef = "" } = {}) {
  const rootResult = spawnSync("git", ["rev-parse", "--show-toplevel"], {
    cwd,
    encoding: "utf8",
  });

  if (rootResult.status !== 0) {
    throw new Error((rootResult.stderr || rootResult.stdout || "Failed to resolve git root").trim());
  }

  const repoRoot = rootResult.stdout.trim();
  const diffArgs = ["diff", "--name-only"];
  if (baseRef) {
    diffArgs.push(baseRef);
  }
  diffArgs.push("--");

  const diffResult = spawnSync("git", diffArgs, {
    cwd: repoRoot,
    encoding: "utf8",
  });

  if (diffResult.status !== 0) {
    throw new Error((diffResult.stderr || diffResult.stdout || "Failed to read git diff").trim());
  }

  return diffResult.stdout
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean)
    .map((filePath) => path.resolve(repoRoot, filePath));
}

function analyzeFile(filePath, options) {
  const fileContent = fs.readFileSync(filePath, "utf8");
  const styleBlocks = extractStyleBlocks(fileContent, filePath);
  const fileErrors = [];

  for (const block of styleBlocks) {
    const result = analyzeContent(block, { ...options, filePath });
    fileErrors.push(...result.errors);
  }

  return fileErrors;
}

function parseCliArgs(args) {
  const parsed = {
    strict: false,
    targetDir: path.resolve(process.cwd(), "src/views/artdeco-pages"),
    hasExplicitTargetDir: false,
    targetFiles: [],
    changedFiles: [],
    changedFromGit: false,
    baseRef: "",
    literalAllowList: ["0px", "1px"],
    checkLiterals: true,
    forbidLegacyTokens: false,
    forbidLegacySass: false,
    forbidLegacyTypography: false,
  };

  for (let index = 0; index < args.length; index += 1) {
    const arg = args[index];
    if (arg === "--strict") {
      parsed.strict = true;
      continue;
    }
    if (arg === "--target-dir" && args[index + 1]) {
      parsed.targetDir = path.resolve(process.cwd(), args[index + 1]);
      parsed.hasExplicitTargetDir = true;
      index += 1;
      continue;
    }
    if (arg === "--target-file" && args[index + 1]) {
      parsed.targetFiles.push(path.resolve(process.cwd(), args[index + 1]));
      index += 1;
      continue;
    }
    if (arg === "--changed-file" && args[index + 1]) {
      parsed.changedFiles.push(path.resolve(process.cwd(), args[index + 1]));
      index += 1;
      continue;
    }
    if (arg === "--changed-from-git") {
      parsed.changedFromGit = true;
      continue;
    }
    if (arg === "--base-ref" && args[index + 1]) {
      parsed.baseRef = args[index + 1];
      index += 1;
      continue;
    }
    if (arg === "--allow-px" && args[index + 1]) {
      parsed.literalAllowList = args[index + 1]
        .split(",")
        .map((item) => item.trim())
        .filter(Boolean);
      index += 1;
      continue;
    }
    if (arg === "--skip-literal-checks") {
      parsed.checkLiterals = false;
      continue;
    }
    if (arg === "--forbid-legacy-tokens") {
      parsed.forbidLegacyTokens = true;
      continue;
    }
    if (arg === "--forbid-legacy-sass") {
      parsed.forbidLegacySass = true;
      continue;
    }
    if (arg === "--forbid-legacy-typography") {
      parsed.forbidLegacyTypography = true;
    }
  }

  return parsed;
}

function runCli() {
  const cli = parseCliArgs(process.argv.slice(2));
  let changedFiles = [...cli.changedFiles];

  if (cli.changedFromGit) {
    try {
      changedFiles = [...changedFiles, ...resolveGitChangedFiles({ cwd: process.cwd(), baseRef: cli.baseRef })];
    } catch (error) {
      console.error(`[check-artdeco-tokens] ${error.message}`);
      process.exit(1);
    }
  }

  const files = resolveTargetFiles({
    targetDir: cli.targetDir,
    targetFiles: cli.targetFiles,
    includeTargetDir: cli.hasExplicitTargetDir,
    changedFiles,
  });
  if (files.length === 0) {
    console.log("No files found to check.");
    process.exit(0);
  }

  const allErrors = [];
  for (const filePath of files) {
    const errors = analyzeFile(filePath, {
      strict: cli.strict,
      literalAllowList: cli.literalAllowList,
      checkLiterals: cli.checkLiterals,
      forbidLegacyTokens: cli.forbidLegacyTokens,
      forbidLegacySass: cli.forbidLegacySass,
      forbidLegacyTypography: cli.forbidLegacyTypography,
    });
    allErrors.push(...errors);
  }

  if (allErrors.length > 0) {
    allErrors.forEach((error) => console.error(error));
    console.error("ArtDeco Token Validation Failed.");
    process.exit(1);
  }

  console.log("ArtDeco Token Validation Passed.");
}

if (require.main === module) {
  runCli();
}

module.exports = {
  analyzeContent,
  analyzeFile,
  extractStyleBlocks,
  listTargetFiles,
  resolveTargetFiles,
  resolveGitChangedFiles,
  parseCliArgs,
};
