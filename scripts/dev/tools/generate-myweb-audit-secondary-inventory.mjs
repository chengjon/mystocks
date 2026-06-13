#!/usr/bin/env node

import { mkdirSync, readFileSync, readdirSync, writeFileSync } from "node:fs"
import { dirname, join, relative, resolve } from "node:path"
import { fileURLToPath } from "node:url"

const __filename = fileURLToPath(import.meta.url)
const __dirname = dirname(__filename)
const PROJECT_ROOT = resolve(__dirname, "../../..")
const VIEWS_ROOT = join(PROJECT_ROOT, "web/frontend/src/views")
const ROUTER_FILE = join(PROJECT_ROOT, "web/frontend/src/router/index.ts")
const DEFAULT_JSON_OUTPUT = join(
  PROJECT_ROOT,
  ".claude/skills/myweb-audit/references/secondary-view-inventory.json",
)
const DEFAULT_MD_OUTPUT = join(
  PROJECT_ROOT,
  ".claude/skills/myweb-audit/references/secondary-view-inventory.md",
)

function walkVueFiles(rootPath) {
  const output = []

  for (const entry of readdirSync(rootPath, { withFileTypes: true })) {
    const absolutePath = join(rootPath, entry.name)
    if (entry.isDirectory()) {
      output.push(...walkVueFiles(absolutePath))
      continue
    }

    if (entry.isFile() && entry.name.endsWith(".vue")) {
      output.push(relative(VIEWS_ROOT, absolutePath).replace(/\\/g, "/"))
    }
  }

  return output.sort()
}

function collectRoutedViews() {
  const routerSource = readFileSync(ROUTER_FILE, "utf8")
  const routed = new Set()

  for (const match of routerSource.matchAll(/import\(['"]@\/views\/([^'"]+)['"]\)/g)) {
    routed.add(match[1])
  }

  for (const match of routerSource.matchAll(/from\s+['"]@\/views\/([^'"]+)['"]/g)) {
    routed.add(match[1])
  }

  return routed
}

function classifyInventoryEntry(viewPath) {
  if (
    viewPath.startsWith("demo/") ||
    viewPath.startsWith("examples/") ||
    viewPath.startsWith("errors/") ||
    /(^|\/)[^/]*demo[^/]*\//i.test(viewPath) ||
    /(?:Demo|Test|Showcase|SkeletonUsage|MinimalTest|PageTitleDemo|PyprofilingDemo)\.vue$/.test(viewPath)
  ) {
    return "Demo废弃"
  }

  if (
    viewPath.startsWith("artdeco-pages/") ||
    viewPath.startsWith("components/") ||
    viewPath.includes("/components/") ||
    viewPath.includes("-tabs/") ||
    viewPath.startsWith("monitoring/") ||
    viewPath.startsWith("stocks/")
  ) {
    return "内嵌壳层"
  }

  return "候选待审"
}

function deriveLayer(viewPath) {
  if (viewPath.startsWith("artdeco-pages/")) {
    return "artdeco-embedded"
  }

  if (viewPath.startsWith("demo/") || viewPath.startsWith("examples/") || viewPath.startsWith("errors/")) {
    return "demo"
  }

  if (viewPath.includes("/")) {
    return viewPath.split("/")[0]
  }

  return "top-level"
}

function scanHeuristics(source) {
  const hasSelector =
    /(selected[A-Z]\w*|active[A-Z]\w*|current[A-Z]\w*|watch\(|v-model=.*select|<el-select|<select|route\.query|route\.params|strategyId|symbol|accountId|watchlistId|period\b)/.test(
      source,
    )
  const hasStatsStrip =
    /(stats-strip|ArtDecoStatCard|stat-card|metric-card|indicator-card|summary-card|hero-meta|module-meta|REQ_ID|TRACE_ID|UPDATED|COUNT:|ROWS:)/.test(
      source,
    )
  const usesSharedComposable =
    /(from ['"]@\/composables\/|from ['"]@\/views\/composables\/|from ['"]\.\.?\/composables\/|from ['"]\.\/composables\/)/.test(
      source,
    )
  const hasFallbackLiterals =
    /(\|\|\s*['"]N\/A['"]|\|\|\s*['"]--['"]|\|\|\s*0\b|\|\|\s*\[\]|\?\?\s*['"]N\/A['"]|\?\?\s*0\b)/.test(source)

  return {
    hasSelector,
    hasStatsStrip,
    usesSharedComposable,
    hasFallbackLiterals,
  }
}

function derivePriority(classification, heuristics) {
  const hitCount = Object.values(heuristics).filter(Boolean).length

  if (classification === "Demo废弃") {
    return "L"
  }

  if (classification === "候选待审" && hitCount >= 1) {
    return "H"
  }

  if (classification === "内嵌壳层" && hitCount >= 1) {
    return "M"
  }

  if (classification === "候选待审") {
    return "M"
  }

  return "L"
}

function buildRecord(viewPath) {
  const absolutePath = join(VIEWS_ROOT, viewPath)
  const source = readFileSync(absolutePath, "utf8")
  const classification = classifyInventoryEntry(viewPath)
  const heuristics = scanHeuristics(source)
  const hitLabels = [
    heuristics.hasStatsStrip ? "stats-strip" : null,
    heuristics.hasSelector ? "selector" : null,
    heuristics.hasFallbackLiterals ? "fallback-literal" : null,
    heuristics.usesSharedComposable ? "shared-composable" : null,
  ].filter(Boolean)

  return {
    pagePath: `web/frontend/src/views/${viewPath}`,
    layer: deriveLayer(viewPath),
    classification,
    hasSelector: heuristics.hasSelector,
    hasStatsStrip: heuristics.hasStatsStrip,
    usesSharedComposable: heuristics.usesSharedComposable,
    priority: derivePriority(classification, heuristics),
    heuristicHits: hitLabels,
  }
}

function summarize(records, totalViews, routedViews) {
  const byClassification = records.reduce((accumulator, record) => {
    accumulator[record.classification] = (accumulator[record.classification] ?? 0) + 1
    return accumulator
  }, {})

  const byPriority = records.reduce((accumulator, record) => {
    accumulator[record.priority] = (accumulator[record.priority] ?? 0) + 1
    return accumulator
  }, {})

  return {
    generatedAt: new Date().toISOString(),
    totalViews,
    routedViews,
    unroutedViews: records.length,
    byClassification,
    byPriority,
    highPriorityShortlistCount: records.filter((record) => record.priority === "H").length,
  }
}

function renderMarkdown(summary, records) {
  const shortlist = records
    .filter((record) => record.priority === "H")
    .sort((left, right) => left.pagePath.localeCompare(right.pagePath))

  const orderedRecords = [...records].sort((left, right) => {
    const priorityOrder = { H: 0, M: 1, L: 2 }
    const priorityDiff = priorityOrder[left.priority] - priorityOrder[right.priority]
    if (priorityDiff !== 0) {
      return priorityDiff
    }

    const classDiff = left.classification.localeCompare(right.classification, "zh-Hans-CN")
    if (classDiff !== 0) {
      return classDiff
    }

    return left.pagePath.localeCompare(right.pagePath)
  })

  const lines = [
    "# Secondary View Inventory",
    "",
    "这是 `myweb-audit v2.1` 的二级资产库存清单。",
    "",
    "用途：",
    "- canonical route coverage matrix 清空 `?` 之后，作为第二阶段 backlog 入口",
    "- 按 `候选待审 / 内嵌壳层 / Demo废弃` 三分类沉淀非主路由页面",
    "- 直接复用 4 个启发式命中特征筛选高优 backlog",
    "",
    "固定输出字段：页面路径、所属层级、是否含 selector、是否有 stats-strip / 指标卡、是否复用公共 composable、优先级标记。",
    "",
    "## Summary",
    "",
    `- generated_at: \`${summary.generatedAt}\``,
    `- total_views: \`${summary.totalViews}\``,
    `- routed_views: \`${summary.routedViews}\``,
    `- unrouted_views: \`${summary.unroutedViews}\``,
    `- classification_counts: \`候选待审=${summary.byClassification["候选待审"] ?? 0} / 内嵌壳层=${summary.byClassification["内嵌壳层"] ?? 0} / Demo废弃=${summary.byClassification["Demo废弃"] ?? 0}\``,
    `- priority_counts: \`H=${summary.byPriority.H ?? 0} / M=${summary.byPriority.M ?? 0} / L=${summary.byPriority.L ?? 0}\``,
    "",
    "## High-Priority Shortlist",
    "",
    "| 页面路径 | 所属层级 | 分类 | selector | stats-strip/指标卡 | 公共 composable | 优先级 | 命中特征 |",
    "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ...shortlist.map((record) =>
      `| \`${record.pagePath}\` | ${record.layer} | ${record.classification} | ${record.hasSelector ? "Y" : "-"} | ${record.hasStatsStrip ? "Y" : "-"} | ${record.usesSharedComposable ? "Y" : "-"} | ${record.priority} | ${record.heuristicHits.join(", ")} |`,
    ),
    "",
    "## Full Inventory",
    "",
    "| 页面路径 | 所属层级 | 分类 | selector | stats-strip/指标卡 | 公共 composable | 优先级 | 命中特征 |",
    "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ...orderedRecords.map((record) =>
      `| \`${record.pagePath}\` | ${record.layer} | ${record.classification} | ${record.hasSelector ? "Y" : "-"} | ${record.hasStatsStrip ? "Y" : "-"} | ${record.usesSharedComposable ? "Y" : "-"} | ${record.priority} | ${record.heuristicHits.join(", ") || "-"} |`,
    ),
    "",
  ]

  return lines.join("\n")
}

function parseArgs(argv) {
  const options = {
    jsonOutput: DEFAULT_JSON_OUTPUT,
    markdownOutput: DEFAULT_MD_OUTPUT,
  }

  for (let index = 0; index < argv.length; index += 1) {
    const token = argv[index]

    if (token === "--json-output") {
      options.jsonOutput = resolve(argv[index + 1])
      index += 1
      continue
    }

    if (token === "--markdown-output") {
      options.markdownOutput = resolve(argv[index + 1])
      index += 1
      continue
    }

    throw new Error(`Unknown argument: ${token}`)
  }

  return options
}

function writeOutput(filePath, content) {
  mkdirSync(dirname(filePath), { recursive: true })
  writeFileSync(filePath, content, "utf8")
}

function main() {
  const options = parseArgs(process.argv.slice(2))
  const allViews = walkVueFiles(VIEWS_ROOT)
  const routedViews = collectRoutedViews()
  const records = allViews.filter((viewPath) => !routedViews.has(viewPath)).map(buildRecord)
  const summary = summarize(records, allViews.length, routedViews.size)
  const payload = { summary, records }

  writeOutput(options.jsonOutput, JSON.stringify(payload, null, 2))
  writeOutput(options.markdownOutput, renderMarkdown(summary, records))

  console.log(
    JSON.stringify(
      {
        jsonOutput: relative(PROJECT_ROOT, options.jsonOutput).replace(/\\/g, "/"),
        markdownOutput: relative(PROJECT_ROOT, options.markdownOutput).replace(/\\/g, "/"),
        ...summary,
      },
      null,
      2,
    ),
  )
}

main()
