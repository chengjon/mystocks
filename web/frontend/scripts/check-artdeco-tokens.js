const fs = require("fs");
const path = require("path");

const COLOR_LITERAL_REGEX = /#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})\b|rgb\s*\(|hsl\s*\(/;
const PX_LITERAL_REGEX = /\b\d+px\b/;
const DUPLICATE_PROP_REGEX = /^\s*(--artdeco-[a-zA-Z0-9-]+)\s*:/;

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
  const strict = Boolean(options?.strict);
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

      if (/\.(vue|scss|css)$/.test(entry.name)) {
        results.push(fullPath);
      }
    }
  };

  walk(targetDir);
  return results;
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
    literalAllowList: ["0px", "1px"],
  };

  for (let index = 0; index < args.length; index += 1) {
    const arg = args[index];
    if (arg === "--strict") {
      parsed.strict = true;
      continue;
    }
    if (arg === "--target-dir" && args[index + 1]) {
      parsed.targetDir = path.resolve(process.cwd(), args[index + 1]);
      index += 1;
      continue;
    }
    if (arg === "--allow-px" && args[index + 1]) {
      parsed.literalAllowList = args[index + 1]
        .split(",")
        .map((item) => item.trim())
        .filter(Boolean);
      index += 1;
    }
  }

  return parsed;
}

function runCli() {
  const cli = parseCliArgs(process.argv.slice(2));
  const files = listTargetFiles(cli.targetDir);
  if (files.length === 0) {
    console.log("No files found to check.");
    process.exit(0);
  }

  const allErrors = [];
  for (const filePath of files) {
    const errors = analyzeFile(filePath, {
      strict: cli.strict,
      literalAllowList: cli.literalAllowList,
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
  parseCliArgs,
};
