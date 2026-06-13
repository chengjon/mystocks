import test from "node:test"
import assert from "node:assert/strict"
import { spawnSync } from "node:child_process"
import { mkdtempSync, mkdirSync, rmSync, writeFileSync } from "node:fs"
import { tmpdir } from "node:os"
import { join, resolve } from "node:path"

const PROJECT_ROOT = resolve(import.meta.dirname, "../../..", "..")
const SCRIPT_PATH = resolve(PROJECT_ROOT, "scripts/dev/tools/validate-myweb-audit-skill.mjs")

const REQUIRED_FIXTURE_FILES = {
  "package.json": JSON.stringify(
    {
      scripts: {
        "generate:myweb-audit:secondary-inventory": "node scripts/dev/tools/generate-myweb-audit-secondary-inventory.mjs",
        "validate:myweb-audit:skill": "node scripts/dev/tools/validate-myweb-audit-skill.mjs",
        "test:myweb-audit:skill":
          "node --test scripts/dev/tools/__node_tests__/validateMywebAuditSkill.test.mjs && npm run validate:myweb-audit:skill",
      },
    },
    null,
    2,
  ),
  ".github/workflows/myweb-audit-skill-governance.yml": `name: MyWeb Audit Skill Governance
on:
  pull_request:
    paths:
      - '.claude/skills/myweb-audit/**'
      - 'scripts/dev/tools/generate-myweb-audit-secondary-inventory.mjs'
jobs:
  validate-myweb-audit-skill:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm run generate:myweb-audit:secondary-inventory
      - run: npm run test:myweb-audit:skill
`,
  ".claude/skills/myweb-audit/SKILL.md":
    "Current major edition: `v2.1`.\nSee route-truth-operations.md for the v2 operator policy.\n",
  ".claude/skills/myweb-audit/references/route-truth-operations.md": "# route-truth-operations\n",
  ".claude/skills/myweb-audit/references/route-truth-casebook.md":
    "This is a representative precedent library and not a full batch ledger.\n",
  ".claude/skills/myweb-audit/references/route-truth-coverage-matrix.md":
    "This is next-pass planning truth and should not be treated as a free-form changelog.\n",
  ".claude/skills/myweb-audit/references/secondary-view-inventory.md":
    "# Secondary View Inventory\nGenerated secondary inventory truth.\n",
  ".claude/skills/myweb-audit/references/secondary-view-inventory.json": JSON.stringify(
    {
      summary: { unroutedViews: 0 },
      records: [],
    },
    null,
    2,
  ),
  ".claude/skills/myweb-audit/references/CHANGELOG.md": "## v2.1 - 2026-05-07\n",
  ".claude/skills/myweb-audit/references/batching-rules.md": "Read route-truth-operations.md before batching.\n",
  ".claude/skills/myweb-audit/references/audit-checklist.md": "Read route-truth-operations.md before auditing.\n",
  ".claude/skills/myweb-audit/references/ARTIFACT_QUICK_REFERENCE.md":
    "Read route-truth-operations.md before validating artifacts.\n",
  ".claude/agents/myweb-audit-route-inventory.md":
    "Read route-truth-operations.md, route-truth-coverage-matrix.md, and secondary-view-inventory.md before planning inventory.\n",
  ".claude/agents/myweb-audit-data-state-audit.md": "Read route-truth-operations.md before auditing.\n",
  ".claude/agents/myweb-audit-functional-audit.md": "Read route-truth-operations.md before auditing.\n",
  ".claude/agents/myweb-audit-responsive-a11y-audit.md": "Read route-truth-operations.md before auditing.\n",
  ".claude/agents/myweb-audit-visual-artdeco-audit.md": "Read route-truth-operations.md before auditing.\n",
  "scripts/dev/tools/generate-myweb-audit-secondary-inventory.mjs":
    "const output = ['secondary-view-inventory.md', 'secondary-view-inventory.json']\n",
}

function writeFixtureTree(rootPath, fileMap) {
  for (const [relativePath, content] of Object.entries(fileMap)) {
    const absolutePath = join(rootPath, relativePath)
    mkdirSync(resolve(absolutePath, ".."), { recursive: true })
    writeFileSync(absolutePath, content, "utf8")
  }
}

test("validate-myweb-audit-skill emits structured success checks for the current repo", () => {
  const result = spawnSync(process.execPath, [SCRIPT_PATH, "--json"], {
    cwd: PROJECT_ROOT,
    encoding: "utf8",
  })

  assert.equal(result.status, 0, `expected exit 0, got ${result.status}\n${result.stderr}`)

  const payload = JSON.parse(result.stdout)
  assert.equal(payload.success, true)

  const checkIds = new Set(payload.checks.map((entry) => entry.id))
  assert.deepEqual(
    checkIds,
    new Set([
      "required-files-exist",
      "current-version-sync",
      "operations-linkage",
        "casebook-role-note",
        "matrix-role-note",
        "agent-linkage",
        "secondary-inventory-linkage",
        "tool-linkage",
      ]),
  )
})

test("validate-myweb-audit-skill fails when a fixture breaks the operations linkage contract", (t) => {
  const fixtureRoot = mkdtempSync(join(tmpdir(), "validate-myweb-audit-skill-"))
  t.after(() => rmSync(fixtureRoot, { recursive: true, force: true }))

  writeFixtureTree(fixtureRoot, {
    ...REQUIRED_FIXTURE_FILES,
    ".claude/skills/myweb-audit/references/audit-checklist.md": "This fixture intentionally omits the operations linkage.\n",
  })

  const result = spawnSync(process.execPath, [SCRIPT_PATH, "--json", "--root", fixtureRoot], {
    cwd: PROJECT_ROOT,
    encoding: "utf8",
  })

  assert.equal(result.status, 1, `expected exit 1, got ${result.status}\n${result.stderr}`)

  const payload = JSON.parse(result.stdout)
  assert.equal(payload.success, false)

  const operationsCheck = payload.checks.find((entry) => entry.id === "operations-linkage")
  assert.ok(operationsCheck)
  assert.equal(operationsCheck.ok, false)
  assert.match(operationsCheck.detail, /audit-checklist\.md/)
})

test("validate-myweb-audit-skill fails when a fixture breaks the workflow or package tool linkage", (t) => {
  const fixtureRoot = mkdtempSync(join(tmpdir(), "validate-myweb-audit-skill-"))
  t.after(() => rmSync(fixtureRoot, { recursive: true, force: true }))

  writeFixtureTree(fixtureRoot, {
    ...REQUIRED_FIXTURE_FILES,
    ".github/workflows/myweb-audit-skill-governance.yml": `name: MyWeb Audit Skill Governance
on:
  pull_request:
    paths:
      - '.claude/skills/myweb-audit/**'
jobs:
  validate-myweb-audit-skill:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm run validate:myweb-audit:skill
`,
  })

  const result = spawnSync(process.execPath, [SCRIPT_PATH, "--json", "--root", fixtureRoot], {
    cwd: PROJECT_ROOT,
    encoding: "utf8",
  })

  assert.equal(result.status, 1, `expected exit 1, got ${result.status}\n${result.stderr}`)

  const payload = JSON.parse(result.stdout)
  assert.equal(payload.success, false)

  const toolLinkageCheck = payload.checks.find((entry) => entry.id === "tool-linkage")
  assert.ok(toolLinkageCheck)
  assert.equal(toolLinkageCheck.ok, false)
  assert.match(toolLinkageCheck.detail, /test:myweb-audit:skill/)
})
