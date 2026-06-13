#!/usr/bin/env node

import { readFileSync, existsSync } from 'fs'
import { dirname, extname, join, resolve } from 'path'
import { fileURLToPath } from 'url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = dirname(__filename)
const PROJECT_ROOT = resolve(__dirname, '../../..')
const yamlModulePath = join(PROJECT_ROOT, 'web/frontend/node_modules/js-yaml/index.js')
const { load: loadYaml } = await import(yamlModulePath)

const SCHEMA_PATHS = {
  manifest: join(PROJECT_ROOT, '.claude/skills/myweb-audit/references/manifest-schema.json'),
  findings: join(PROJECT_ROOT, '.claude/skills/myweb-audit/references/findings-schema.json'),
  merged: join(PROJECT_ROOT, '.claude/skills/myweb-audit/references/merged-findings-schema.json'),
  approval: join(PROJECT_ROOT, '.claude/skills/myweb-audit/references/repair-approval-schema.json'),
}

function printHelp() {
  console.log(`Usage:
  node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema <manifest|findings|merged|approval> --file <path> [--json]
  node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --all --manifest <path> --findings <path> --merged <path> [--approval <path>] [--json]
  node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --all --run-id <audit-run-id> --batch-id <batch-id> [--json]
  node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --from-manifest <manifest-path> [--json]

Examples:
  node scripts/dev/tools/validate-myweb-audit-artifacts.mjs \\
    --schema manifest \\
    --file docs/reports/quality/myweb-audit/audit-20260425-01/manifests/data-batch-01-manifest.yaml

  node scripts/dev/tools/validate-myweb-audit-artifacts.mjs \\
    --schema findings \\
    --file docs/reports/quality/myweb-audit/audit-20260425-01/findings/data-batch-01-raw-findings.yaml

  node scripts/dev/tools/validate-myweb-audit-artifacts.mjs \\
    --schema merged \\
    --file docs/reports/quality/myweb-audit/audit-20260425-01/findings/data-batch-01-merged-findings.yaml

  node scripts/dev/tools/validate-myweb-audit-artifacts.mjs \\
    --schema approval \\
    --file docs/reports/quality/myweb-audit/audit-20260425-01/approvals/data-batch-01-repair-approval.yaml

  node scripts/dev/tools/validate-myweb-audit-artifacts.mjs \\
    --all \\
    --manifest docs/reports/quality/myweb-audit/audit-20260425-01/manifests/data-batch-01-manifest.yaml \\
    --findings docs/reports/quality/myweb-audit/audit-20260425-01/findings/data-batch-01-raw-findings.yaml \\
    --merged docs/reports/quality/myweb-audit/audit-20260425-01/findings/data-batch-01-merged-findings.yaml \\
    --approval docs/reports/quality/myweb-audit/audit-20260425-01/approvals/data-batch-01-repair-approval.yaml

  node scripts/dev/tools/validate-myweb-audit-artifacts.mjs \\
    --all \\
    --run-id audit-20260425-01 \\
    --batch-id data-batch-01

  node scripts/dev/tools/validate-myweb-audit-artifacts.mjs \\
    --from-manifest docs/reports/quality/myweb-audit/audit-20260425-01/manifests/data-batch-01-manifest.yaml
`)
}

function parseArgs(argv) {
  const options = {
    schema: null,
    file: null,
    manifest: null,
    findings: null,
    merged: null,
    approval: null,
    runId: null,
    batchId: null,
    fromManifest: null,
    all: false,
    json: false,
    help: false,
  }

  for (let index = 0; index < argv.length; index += 1) {
    const token = argv[index]

    if (token === '--schema') {
      options.schema = argv[index + 1] ?? null
      index += 1
      continue
    }

    if (token === '--file') {
      options.file = argv[index + 1] ?? null
      index += 1
      continue
    }

    if (token === '--manifest') {
      options.manifest = argv[index + 1] ?? null
      index += 1
      continue
    }

    if (token === '--findings') {
      options.findings = argv[index + 1] ?? null
      index += 1
      continue
    }

    if (token === '--merged') {
      options.merged = argv[index + 1] ?? null
      index += 1
      continue
    }

    if (token === '--approval') {
      options.approval = argv[index + 1] ?? null
      index += 1
      continue
    }

    if (token === '--run-id') {
      options.runId = argv[index + 1] ?? null
      index += 1
      continue
    }

    if (token === '--batch-id') {
      options.batchId = argv[index + 1] ?? null
      index += 1
      continue
    }

    if (token === '--from-manifest') {
      options.fromManifest = argv[index + 1] ?? null
      index += 1
      continue
    }

    if (token === '--all') {
      options.all = true
      continue
    }

    if (token === '--json') {
      options.json = true
      continue
    }

    if (token === '--help' || token === '-h') {
      options.help = true
      continue
    }

    throw new Error(`Unknown argument: ${token}`)
  }

  return options
}

function readStructuredFile(filePath) {
  const absolutePath = resolve(PROJECT_ROOT, filePath)
  if (!existsSync(absolutePath)) {
    throw new Error(`File not found: ${absolutePath}`)
  }

  const source = readFileSync(absolutePath, 'utf8')
  const extension = extname(absolutePath).toLowerCase()

  if (extension === '.json') {
    return { absolutePath, payload: JSON.parse(source) }
  }

  if (extension === '.yaml' || extension === '.yml') {
    return { absolutePath, payload: loadYaml(source) }
  }

  throw new Error(`Unsupported file extension: ${extension}`)
}

function createValidator(schemaName) {
  const schemaPath = SCHEMA_PATHS[schemaName]
  if (!schemaPath) {
    throw new Error(`Unsupported schema name: ${schemaName}`)
  }

  const schema = JSON.parse(readFileSync(schemaPath, 'utf8'))
  return {
    schemaPath,
    schema,
  }
}

function joinInstancePath(basePath, token) {
  if (token.startsWith('[')) {
    return `${basePath}${token}`
  }
  return basePath === '/' ? `/${token}` : `${basePath}/${token}`
}

function normalizeType(type) {
  if (type === 'integer') {
    return 'number'
  }
  return type
}

function matchesType(value, type) {
  if (type === 'null') {
    return value === null
  }
  if (type === 'array') {
    return Array.isArray(value)
  }
  if (type === 'integer') {
    return Number.isInteger(value)
  }
  if (type === 'object') {
    return typeof value === 'object' && value !== null && !Array.isArray(value)
  }
  return typeof value === normalizeType(type)
}

function validateAgainstSchema(value, schema, instancePath = '/', schemaPath = '#') {
  const errors = []

  if (!schema || typeof schema !== 'object') {
    return errors
  }

  if (Array.isArray(schema.type)) {
    const matched = schema.type.some((entry) => matchesType(value, entry))
    if (!matched) {
      errors.push({
        instancePath,
        schemaPath: `${schemaPath}/type`,
        message: `should be one of types: ${schema.type.join(', ')}`,
      })
      return errors
    }
  } else if (schema.type && !matchesType(value, schema.type)) {
    errors.push({
      instancePath,
      schemaPath: `${schemaPath}/type`,
      message: `should be ${schema.type}`,
    })
    return errors
  }

  if (schema.enum && !schema.enum.includes(value)) {
    errors.push({
      instancePath,
      schemaPath: `${schemaPath}/enum`,
      message: `should be one of: ${schema.enum.join(', ')}`,
    })
  }

  if (typeof value === 'string') {
    if (typeof schema.minLength === 'number' && value.length < schema.minLength) {
      errors.push({
        instancePath,
        schemaPath: `${schemaPath}/minLength`,
        message: `should NOT be shorter than ${schema.minLength} characters`,
      })
    }

    if (schema.pattern) {
      const regex = new RegExp(schema.pattern)
      if (!regex.test(value)) {
        errors.push({
          instancePath,
          schemaPath: `${schemaPath}/pattern`,
          message: `should match pattern ${schema.pattern}`,
        })
      }
    }
  }

  if (typeof value === 'number' && typeof schema.minimum === 'number' && value < schema.minimum) {
    errors.push({
      instancePath,
      schemaPath: `${schemaPath}/minimum`,
      message: `should be >= ${schema.minimum}`,
    })
  }

  if (Array.isArray(value)) {
    if (typeof schema.minItems === 'number' && value.length < schema.minItems) {
      errors.push({
        instancePath,
        schemaPath: `${schemaPath}/minItems`,
        message: `should NOT have fewer than ${schema.minItems} items`,
      })
    }

    if (schema.items) {
      value.forEach((entry, index) => {
        errors.push(...validateAgainstSchema(
          entry,
          schema.items,
          joinInstancePath(instancePath, `[${index}]`),
          `${schemaPath}/items`,
        ))
      })
    }
  }

  if (typeof value === 'object' && value !== null && !Array.isArray(value)) {
    const propertyNames = Object.keys(value)

    if (Array.isArray(schema.required)) {
      schema.required.forEach((field) => {
        if (!(field in value)) {
          errors.push({
            instancePath,
            schemaPath: `${schemaPath}/required`,
            message: `should have required property '${field}'`,
          })
        }
      })
    }

    if (schema.additionalProperties === false && schema.properties) {
      propertyNames.forEach((field) => {
        if (!(field in schema.properties)) {
          errors.push({
            instancePath: joinInstancePath(instancePath, field),
            schemaPath: `${schemaPath}/additionalProperties`,
            message: `should NOT have additional property '${field}'`,
          })
        }
      })
    }

    if (schema.properties) {
      Object.entries(schema.properties).forEach(([field, childSchema]) => {
        if (field in value) {
          errors.push(...validateAgainstSchema(
            value[field],
            childSchema,
            joinInstancePath(instancePath, field),
            `${schemaPath}/properties/${field}`,
          ))
        }
      })
    }
  }

  return errors
}

function validatePayload(schemaName, payload, schema) {
  if ((schemaName === 'findings' || schemaName === 'merged' || schemaName === 'approval') && Array.isArray(payload)) {
    const errors = []
    payload.forEach((entry, index) => {
      errors.push(...validateAgainstSchema(entry, schema, `/[${index}]`, '#'))
    })

    return {
      valid: errors.length === 0,
      entriesChecked: payload.length,
      errors,
    }
  }

  const errors = validateAgainstSchema(payload, schema, '/', '#')
  return {
    valid: errors.length === 0,
    entriesChecked: 1,
    errors,
  }
}

function validateOne(schemaName, filePath) {
  const { absolutePath, payload } = readStructuredFile(filePath)
  const { schemaPath, schema } = createValidator(schemaName)
  const result = validatePayload(schemaName, payload, schema)

  return {
    schema: schemaName,
    schemaPath,
    file: absolutePath,
    entriesChecked: result.entriesChecked,
    valid: result.valid,
    errors: result.errors,
  }
}

function resolveBatchArtifactPaths(runId, batchId) {
  const root = join(PROJECT_ROOT, 'docs/reports/quality/myweb-audit', runId)
  return {
    manifest: join(root, 'manifests', `${batchId}-manifest.yaml`),
    findings: join(root, 'findings', `${batchId}-raw-findings.yaml`),
    merged: join(root, 'findings', `${batchId}-merged-findings.yaml`),
    approval: join(root, 'approvals', `${batchId}-repair-approval.yaml`),
  }
}

function resolvePathsFromManifest(manifestPath) {
  const { absolutePath, payload } = readStructuredFile(manifestPath)

  if (!payload || typeof payload !== 'object' || Array.isArray(payload)) {
    throw new Error(`Manifest payload must be an object: ${absolutePath}`)
  }

  const artifacts = payload.artifacts
  if (!artifacts || typeof artifacts !== 'object' || Array.isArray(artifacts)) {
    throw new Error(`Manifest is missing artifacts object: ${absolutePath}`)
  }

  if (!artifacts.raw_findings || !artifacts.merged_findings) {
    throw new Error(`Manifest must include artifacts.raw_findings and artifacts.merged_findings: ${absolutePath}`)
  }

  return {
    manifest: manifestPath,
    findings: artifacts.raw_findings,
    merged: artifacts.merged_findings,
    approval: artifacts.repair_approval_package ?? null,
  }
}

function main() {
  const options = parseArgs(process.argv.slice(2))
  if (options.help) {
    printHelp()
    process.exit(0)
  }

  if (options.fromManifest) {
    const resolvedPaths = resolvePathsFromManifest(options.fromManifest)
    options.all = true
    options.manifest = resolvedPaths.manifest
    options.findings = resolvedPaths.findings
    options.merged = resolvedPaths.merged
    options.approval = resolvedPaths.approval
  }

  if (options.all) {
    const hasDirectPaths = options.manifest && options.findings && options.merged
    const hasBatchLocator = options.runId && options.batchId

    if (!hasDirectPaths && !hasBatchLocator) {
      printHelp()
      throw new Error('--all requires either explicit artifact paths or both --run-id and --batch-id.')
    }

    if (hasBatchLocator && !hasDirectPaths) {
      const resolvedPaths = resolveBatchArtifactPaths(options.runId, options.batchId)
      options.manifest = resolvedPaths.manifest
      options.findings = resolvedPaths.findings
      options.merged = resolvedPaths.merged
      options.approval = resolvedPaths.approval
    }

    const summaries = [
      validateOne('manifest', options.manifest),
      validateOne('findings', options.findings),
      validateOne('merged', options.merged),
    ]
    if (options.approval) {
      summaries.push(validateOne('approval', options.approval))
    }
    const valid = summaries.every((entry) => entry.valid)

    if (options.json) {
      console.log(JSON.stringify({ valid, results: summaries }, null, 2))
    } else if (valid) {
      console.log(`OK all validations passed (${summaries.map((entry) => `${entry.schema}:${entry.entriesChecked}`).join(', ')})`)
    } else {
      console.error('FAIL one or more validations failed')
      for (const summary of summaries.filter((entry) => !entry.valid)) {
        console.error(`Schema ${summary.schema} failed for ${summary.file}`)
        for (const error of summary.errors) {
          console.error(`- ${error.instancePath}: ${error.message} (${error.schemaPath})`)
        }
      }
    }

    process.exit(valid ? 0 : 1)
  }

  if (!options.schema || !options.file) {
    printHelp()
    throw new Error('Either use --all with three file paths, or provide both --schema and --file.')
  }

  const summary = validateOne(options.schema, options.file)

  if (options.json) {
    console.log(JSON.stringify(summary, null, 2))
  } else if (summary.valid) {
    console.log(`OK ${options.schema} validation passed for ${summary.file} (${summary.entriesChecked} entr${summary.entriesChecked === 1 ? 'y' : 'ies'})`)
  } else {
    console.error(`FAIL ${options.schema} validation failed for ${summary.file}`)
    for (const error of summary.errors) {
      console.error(`- ${error.instancePath}: ${error.message} (${error.schemaPath})`)
    }
  }

  process.exit(summary.valid ? 0 : 1)
}

try {
  main()
} catch (error) {
  console.error(error instanceof Error ? error.message : String(error))
  process.exit(1)
}
