#!/usr/bin/env node

const { spawnSync } = require("node:child_process");

const STABLE_UNIT_TEST_FILES = [
  "tests/unit/config/pageConfig.test.ts",
  "tests/unit/config/lighthouse-mainline-gates.spec.ts",
  "tests/unit/config/testing-mainline-gates.spec.ts",
  "tests/unit/config/visual-chart-gates.spec.ts",
  "tests/unit/config/vitest-msw-gates.spec.ts",
  "tests/unit/components/CommandPalette.test.ts",
  "tests/unit/config/menu-config-strategy-routes.test.ts",
  "tests/unit/layout/BaseLayout.test.ts",
  "tests/unit/layout/DomainLayouts.test.ts",
  "tests/unit/router/PageMigration.test.ts",
  "tests/unit/AStockFeatures.spec.ts",
  "tests/unit/ChartInteraction.spec.ts",
  "tests/unit/port-config-consistency.spec.ts",
  "tests/unit/structure.test.ts",
  "tests/unit/use-strategy.spec.ts",
  "tests/unit/utils/atrading.test.ts",
  "tests/unit/utils/indicators.test.ts",
  "tests/unit/kline-chart.spec.ts",
  "src/api/adapters/marketAdapter.spec.ts",
  "src/api/__tests__/strategy.test.ts",
  "src/api/services/__tests__/dashboardService.spec.ts",
  "src/api/services/__tests__/strategyService.msw.spec.ts",
  "src/api/__tests__/unifiedApiClient.contract.test.ts",
  "tests/unit/scripts/check-artdeco-tokens.spec.ts",
  "tests/unit/scripts/check-e2e-user-locators.spec.ts",
  "tests/unit/scripts/check-type-error-ceiling.spec.ts",
  "tests/unit/scripts/stable-unit-suite.spec.ts",
  "tests/unit/scripts/validate-e2e-setup.spec.ts",
  "tests/unit/workflows/ci-workflow-gates.spec.ts",
  "src/config/__tests__/pageConfig.home.spec.ts",
  "src/router/__tests__/home-route.spec.ts",
  "src/mock/__tests__/backtestWorkbenchMock.spec.ts",
  "src/stores/__tests__/auth-guard.spec.ts",
];

function buildStableVitestArgs() {
  return ["run", ...STABLE_UNIT_TEST_FILES];
}

function runStableUnitSuite({ cwd = process.cwd() } = {}) {
  return spawnSync("npx", ["vitest", ...buildStableVitestArgs()], {
    cwd,
    encoding: "utf8",
    shell: process.platform === "win32",
  });
}

if (require.main === module) {
  const result = runStableUnitSuite();

  if (result.stdout) {
    process.stdout.write(result.stdout);
  }

  if (result.stderr) {
    process.stderr.write(result.stderr);
  }

  if (result.error) {
    console.error(`[stable-unit-suite] Failed to execute Vitest: ${result.error.message}`);
    process.exit(1);
  }

  process.exit(result.status ?? 1);
}

module.exports = {
  STABLE_UNIT_TEST_FILES,
  buildStableVitestArgs,
  runStableUnitSuite,
};
