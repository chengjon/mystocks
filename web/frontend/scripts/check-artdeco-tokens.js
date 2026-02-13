#!/usr/bin/env node

const fs = require("node:fs");
const path = require("node:path");

const CUSTOM_PROPERTY_RE = /(^|[\s;{])(--[a-zA-Z0-9-_]+)\s*:/g;
const LITERAL_RE = /#[0-9a-fA-F]{3,8}\b|rgba?\([^\)]+\)|\b\d*\.?\d+px\b/g;

function extractStyleBlocks(content, filePath) {
  if (!filePath.endsWith(".vue")) {
    return [content];
  }

  const blocks = [];
  const styleTagRe = /<style\b[^>]*>([\s\S]*?)<\/style>/gi;
  let match;

  while ((match = styleTagRe.exec(content)) !== null) {
    blocks.push(match[1]);
  }

  return blocks;
}

function stripComments(content) {
  return content.replace(/\/\*[\s\S]*?\*\//g, "");
}

function lineNumberAt(content, index) {
  return content.slice(0, index).split("\n").length;
}

function analyzeContent(content, options = {}) {
  const strict = Boolean(options.strict);
  const literalAllowList = new Set(options.literalAllowList || []);
  const filePath = options.filePath || "<inline>";

  const cleanContent = stripComments(content);
  const errors = [];
  const propertyLocations = new Map();

  let propertyMatch;
  while ((propertyMatch = CUSTOM_PROPERTY_RE.exec(cleanContent)) !== null) {
    const name = propertyMatch[2];
    const location = {
      line: lineNumberAt(cleanContent, propertyMatch.index),
      filePath,
    };

    if (!propertyLocations.has(name)) {
      propertyLocations.set(name, []);
    }
    propertyLocations.get(name).push(location);
  }

  for (const [name, locations] of propertyLocations.entries()) {
    if (locations.length > 1) {
      errors.push(
        `${filePath}: duplicate custom property '${name}' (${locations.length} definitions)`,
      );
    }
  }

  if (strict) {
    const lines = cleanContent.split("\n");

    lines.forEach((line, idx) => {
      const declarationMatch = line.match(/^\s*([a-zA-Z-]+)\s*:\s*([^;]+);/);
      if (!declarationMatch) {
        return;
      }

      const property = declarationMatch[1];
      const value = declarationMatch[2];
      if (property.startsWith("--")) {
        return;
      }
      if (value.includes("var(--")) {
        return;
      }

      const literals = value.match(LITERAL_RE) || [];
      literals.forEach((literal) => {
        if (!literalAllowList.has(literal)) {
          errors.push(
            `${filePath}:${idx + 1} hardcoded literal value '${literal}' is not allowed in strict mode`,
          );
        }
      });
    });
  }

  return { errors, warnings: [] };
}

function scanFiles(rootDir) {
  const files = [];
  const stack = [rootDir];

  while (stack.length) {
    const current = stack.pop();
    const entries = fs.readdirSync(current, { withFileTypes: true });

    for (const entry of entries) {
      const fullPath = path.join(current, entry.name);
      if (entry.isDirectory()) {
        stack.push(fullPath);
      } else if (/\.(css|scss|vue)$/.test(entry.name)) {
        files.push(fullPath);
      }
    }
  }

  return files;
}

function loadManifestLiteralAllowList() {
  const manifestPath = path.resolve(
    __dirname,
    "../src/styles/artdeco-governance-manifest.json",
  );

  if (!fs.existsSync(manifestPath)) {
    return [];
  }

  try {
    const manifest = JSON.parse(fs.readFileSync(manifestPath, "utf8"));
    return manifest.tokens?.literalAllowList || [];
  } catch (error) {
    return [];
  }
}

function parseArgs(argv) {
  const args = {
    strict: false,
    targetDir: path.resolve(__dirname, "../src"),
    cliAllowList: [],
  };

  argv.forEach((arg) => {
    if (arg === "--strict") {
      args.strict = true;
      return;
    }

    if (arg.startsWith("--path=")) {
      args.targetDir = path.resolve(process.cwd(), arg.replace("--path=", ""));
      return;
    }

    if (arg.startsWith("--allow=")) {
      const values = arg
        .replace("--allow=", "")
        .split(",")
        .map((value) => value.trim())
        .filter(Boolean);
      args.cliAllowList.push(...values);
    }
  });

  return args;
}

function runCli(argv = process.argv.slice(2)) {
  const args = parseArgs(argv);
  const literalAllowList = [
    ...loadManifestLiteralAllowList(),
    ...args.cliAllowList,
  ];

  if (!fs.existsSync(args.targetDir)) {
    console.error(`Target path does not exist: ${args.targetDir}`);
    return 2;
  }

  const files = scanFiles(args.targetDir);
  const errors = [];

  files.forEach((filePath) => {
    const content = fs.readFileSync(filePath, "utf8");
    const styleBlocks = extractStyleBlocks(content, filePath);

    styleBlocks.forEach((styleContent) => {
      const result = analyzeContent(styleContent, {
        strict: args.strict,
        literalAllowList,
        filePath,
      });
      errors.push(...result.errors);
    });
  });

  if (errors.length > 0) {
    errors.forEach((error) => console.error(`ERROR: ${error}`));
    console.error(`ArtDeco token check failed: ${errors.length} violation(s)`);
    return 1;
  }

  console.log(
    `ArtDeco token check passed (${files.length} files scanned, strict=${args.strict})`,
  );
  return 0;
}

if (require.main === module) {
  process.exit(runCli());
}

module.exports = {
  analyzeContent,
  extractStyleBlocks,
  loadManifestLiteralAllowList,
  parseArgs,
  runCli,
  scanFiles,
  stripComments,
};
