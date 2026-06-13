#!/usr/bin/env node

import { existsSync, readFileSync } from "node:fs"
import { dirname, join, resolve } from "node:path"
import { fileURLToPath } from "node:url"

const __filename = fileURLToPath(import.meta.url)
const __dirname = dirname(__filename)
const DEFAULT_PROJECT_ROOT = resolve(__dirname, "../../..")

const REQUIRED_FILES = [
  ".claude/skills/myweb-audit/SKILL.md",
  ".claude/skills/myweb-audit/references/route-truth-operations.md",
  ".claude/skills/myweb-audit/references/route-truth-casebook.md",
  ".claude/skills/myweb-audit/references/route-truth-coverage-matrix.md",
  ".claude/skills/myweb-audit/references/secondary-view-inventory.md",
  ".claude/skills/myweb-audit/references/secondary-view-inventory.json",
  ".claude/skills/myweb-audit/references/CHANGELOG.md",
  ".claude/skills/myweb-audit/references/batching-rules.md",
  ".claude/skills/myweb-audit/references/audit-checklist.md",
  ".claude/skills/myweb-audit/references/ARTIFACT_QUICK_REFERENCE.md",
]

const AGENT_FILES = [
  ".claude/agents/myweb-audit-route-inventory.md",
  ".claude/agents/myweb-audit-data-state-audit.md",
  ".claude/agents/myweb-audit-functional-audit.md",
  ".claude/agents/myweb-audit-responsive-a11y-audit.md",
  ".claude/agents/myweb-audit-visual-artdeco-audit.md",
]

const TOOLING_FILES = [
  "package.json",
  ".github/workflows/myweb-audit-skill-governance.yml",
  "scripts/dev/tools/generate-myweb-audit-secondary-inventory.mjs",
]

function printHelp() {
  console.log(`Usage:
  node scripts/dev/tools/validate-myweb-audit-skill.mjs [--json] [--root <path>]
  node scripts/dev/tools/validate-myweb-audit-skill.mjs --help

Checks:
  - required files exist
  - SKILL current version matches latest v2 changelog entry
  - operations doc is linked from the main v2 operator entrypoints
  - casebook and coverage matrix retain their v2 role notes
  - fixed myweb-audit agents are linked to the operations policy
`)
}

function parseArgs(argv) {
  const options = {
    json: false,
    help: false,
    root: DEFAULT_PROJECT_ROOT,
  }

  for (let index = 0; index < argv.length; index += 1) {
    const token = argv[index]

    if (token === "--json") {
      options.json = true
      continue
    }

    if (token === "--root") {
      const rootPath = argv[index + 1]
      if (!rootPath) {
        throw new Error("Missing value for --root")
      }

      options.root = resolve(rootPath)
      index += 1
      continue
    }

    if (token === "--help" || token === "-h") {
      options.help = true
      continue
    }

    throw new Error(`Unknown argument: ${token}`)
  }

  return options
}

function readRepoFile(rootPath, relativePath) {
  const absolutePath = join(rootPath, relativePath)
  return readFileSync(absolutePath, "utf8")
}

function createCheck(id, ok, detail) {
  return { id, ok, detail }
}

function extractCurrentSkillVersion(skillSource) {
  const match = skillSource.match(/Current major edition:\s*`([^`]+)`\./)
  return match?.[1] ?? null
}

function extractLatestV2Version(changelogSource) {
  const matches = [...changelogSource.matchAll(/^##\s+(v2\.\d+)\s+-/gm)].map((entry) => entry[1])
  if (matches.length === 0) {
    return null
  }

  const sorted = matches.sort((left, right) => {
    const leftVersion = Number.parseInt(left.split(".")[1] ?? "0", 10)
    const rightVersion = Number.parseInt(right.split(".")[1] ?? "0", 10)
    return rightVersion - leftVersion
  })

  return sorted[0] ?? null
}

function validateRequiredFiles(rootPath) {
  const missing = [...REQUIRED_FILES, ...AGENT_FILES].filter((relativePath) => !existsSync(join(rootPath, relativePath)))
  return createCheck(
    "required-files-exist",
    missing.length === 0,
    missing.length === 0 ? "All required v2.1 skill, reference, and agent files exist." : `Missing files: ${missing.join(", ")}`,
  )
}

function validateCurrentVersionSync(skillSource, changelogSource) {
  const skillVersion = extractCurrentSkillVersion(skillSource)
  const changelogVersion = extractLatestV2Version(changelogSource)
  const ok = Boolean(skillVersion) && Boolean(changelogVersion) && skillVersion === changelogVersion

  return createCheck(
    "current-version-sync",
    ok,
    ok
      ? `SKILL current major edition matches latest v2 changelog entry: ${skillVersion}.`
      : `Version mismatch: SKILL=${skillVersion ?? "missing"}, CHANGELOG=${changelogVersion ?? "missing"}.`,
  )
}

function validateOperationsLinkage(fileMap) {
  const expected = [
    ".claude/skills/myweb-audit/SKILL.md",
    ".claude/skills/myweb-audit/references/batching-rules.md",
    ".claude/skills/myweb-audit/references/audit-checklist.md",
    ".claude/skills/myweb-audit/references/ARTIFACT_QUICK_REFERENCE.md",
  ]

  const missing = expected.filter((relativePath) => !fileMap.get(relativePath)?.includes("route-truth-operations.md"))
  return createCheck(
    "operations-linkage",
    missing.length === 0,
    missing.length === 0
      ? "Main v2 operator entrypoints all link to route-truth-operations.md."
      : `Missing operations linkage in: ${missing.join(", ")}`,
  )
}

function validateCasebookRole(casebookSource) {
  const ok =
    casebookSource.includes("representative precedent library") &&
    casebookSource.includes("not a full batch ledger")

  return createCheck(
    "casebook-role-note",
    ok,
    ok
      ? "Casebook declares itself as representative precedent storage, not a batch ledger."
      : "Casebook is missing the v2 role note about representative precedent storage.",
  )
}

function validateMatrixRole(matrixSource) {
  const ok =
    matrixSource.includes("next-pass planning truth") &&
    matrixSource.includes("not as a free-form changelog")

  return createCheck(
    "matrix-role-note",
    ok,
    ok
      ? "Coverage matrix declares next-pass planning truth and changelog boundary."
      : "Coverage matrix is missing the v2 planning-truth or anti-changelog note.",
  )
}

function validateAgentLinkage(fileMap) {
  const missingOperations = AGENT_FILES.filter((relativePath) => !fileMap.get(relativePath)?.includes("route-truth-operations.md"))
  const routeInventory = fileMap.get(".claude/agents/myweb-audit-route-inventory.md") ?? ""
  const missingCoverageInInventory = !routeInventory.includes("route-truth-coverage-matrix.md")

  const ok = missingOperations.length === 0 && !missingCoverageInInventory
  const parts = []
  if (missingOperations.length > 0) {
    parts.push(`missing operations linkage in: ${missingOperations.join(", ")}`)
  }
  if (missingCoverageInInventory) {
    parts.push("route-inventory is missing coverage-matrix linkage")
  }

  return createCheck(
    "agent-linkage",
    ok,
    ok ? "All fixed myweb-audit agents are linked to the v2 operations policy." : parts.join("; "),
  )
}

function validateSecondaryInventoryLinkage(fileMap) {
  const operationsSource = fileMap.get(".claude/skills/myweb-audit/references/route-truth-operations.md") ?? ""
  const routeInventorySource = fileMap.get(".claude/agents/myweb-audit-route-inventory.md") ?? ""
  const generatorSource = fileMap.get("scripts/dev/tools/generate-myweb-audit-secondary-inventory.mjs") ?? ""

  const missing = []
  if (!operationsSource.includes("secondary-view-inventory.md")) {
    missing.push("operations missing secondary-view-inventory linkage")
  }
  if (!routeInventorySource.includes("secondary-view-inventory.md")) {
    missing.push("route-inventory agent missing secondary inventory linkage")
  }
  if (!generatorSource.includes("secondary-view-inventory.md")) {
    missing.push("generator script missing markdown output linkage")
  }
  if (!generatorSource.includes("secondary-view-inventory.json")) {
    missing.push("generator script missing json output linkage")
  }

  return createCheck(
    "secondary-inventory-linkage",
    missing.length === 0,
    missing.length === 0
      ? "Secondary inventory docs, route-inventory guidance, and generator outputs are wired into the v2.1 workflow."
      : missing.join("; "),
  )
}

function validateToolLinkage(fileMap) {
  const packageSource = fileMap.get("package.json") ?? ""
  const workflowSource = fileMap.get(".github/workflows/myweb-audit-skill-governance.yml") ?? ""

  const missingPackageScripts = []
  if (!packageSource.includes('"generate:myweb-audit:secondary-inventory"')) {
    missingPackageScripts.push("generate:myweb-audit:secondary-inventory")
  }
  if (!packageSource.includes('"validate:myweb-audit:skill"')) {
    missingPackageScripts.push("validate:myweb-audit:skill")
  }
  if (!packageSource.includes('"test:myweb-audit:skill"')) {
    missingPackageScripts.push("test:myweb-audit:skill")
  }

  const missingWorkflowLinkage = []
  if (!workflowSource.includes("npm run test:myweb-audit:skill")) {
    missingWorkflowLinkage.push("workflow does not invoke npm run test:myweb-audit:skill")
  }
  if (!workflowSource.includes(".claude/skills/myweb-audit/**")) {
    missingWorkflowLinkage.push("workflow paths do not scope to .claude/skills/myweb-audit/**")
  }
  if (!workflowSource.includes("scripts/dev/tools/generate-myweb-audit-secondary-inventory.mjs")) {
    missingWorkflowLinkage.push("workflow is missing the secondary inventory generator path linkage")
  }
  if (!workflowSource.includes("npm run generate:myweb-audit:secondary-inventory")) {
    missingWorkflowLinkage.push("workflow does not invoke npm run generate:myweb-audit:secondary-inventory")
  }
  if (!workflowSource.includes("scripts/dev/tools/validate-myweb-audit-skill.mjs")) {
    missingWorkflowLinkage.push("workflow is missing the validator script path linkage")
  }

  const ok = missingPackageScripts.length === 0 && missingWorkflowLinkage.length === 0
  const parts = []
  if (missingPackageScripts.length > 0) {
    parts.push(`missing package scripts: ${missingPackageScripts.join(", ")}`)
  }
  if (missingWorkflowLinkage.length > 0) {
    parts.push(missingWorkflowLinkage.join("; "))
  }

  return createCheck(
    "tool-linkage",
    ok,
    ok
      ? "Package scripts and workflow are wired to the myweb-audit skill self-check."
      : parts.join("; "),
  )
}

function runChecks(rootPath) {
  const checkResults = []
  const fileMap = new Map()

  checkResults.push(validateRequiredFiles(rootPath))

  const allFiles = [...REQUIRED_FILES, ...AGENT_FILES, ...TOOLING_FILES]
  for (const relativePath of allFiles) {
    if (existsSync(join(rootPath, relativePath))) {
      fileMap.set(relativePath, readRepoFile(rootPath, relativePath))
    }
  }

  const skillSource = fileMap.get(".claude/skills/myweb-audit/SKILL.md") ?? ""
  const changelogSource = fileMap.get(".claude/skills/myweb-audit/references/CHANGELOG.md") ?? ""
  const casebookSource = fileMap.get(".claude/skills/myweb-audit/references/route-truth-casebook.md") ?? ""
  const matrixSource = fileMap.get(".claude/skills/myweb-audit/references/route-truth-coverage-matrix.md") ?? ""

  checkResults.push(validateCurrentVersionSync(skillSource, changelogSource))
  checkResults.push(validateOperationsLinkage(fileMap))
  checkResults.push(validateCasebookRole(casebookSource))
  checkResults.push(validateMatrixRole(matrixSource))
  checkResults.push(validateAgentLinkage(fileMap))
  checkResults.push(validateSecondaryInventoryLinkage(fileMap))
  checkResults.push(validateToolLinkage(fileMap))

  return checkResults
}

function printHumanSummary(checks) {
  for (const check of checks) {
    const prefix = check.ok ? "PASS" : "FAIL"
    console.log(`${prefix} ${check.id}: ${check.detail}`)
  }
}

function main() {
  const options = parseArgs(process.argv.slice(2))
  if (options.help) {
    printHelp()
    return
  }

  const checks = runChecks(options.root)
  const success = checks.every((check) => check.ok)

  if (options.json) {
    console.log(
      JSON.stringify(
        {
          success,
          checks,
        },
        null,
        2,
      ),
    )
  } else {
    printHumanSummary(checks)
  }

  if (!success) {
    process.exitCode = 1
  }
}

try {
  main()
} catch (error) {
  console.error(error instanceof Error ? error.message : String(error))
  process.exitCode = 1
}
