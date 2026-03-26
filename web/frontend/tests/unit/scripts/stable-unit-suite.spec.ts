import { createRequire } from "node:module";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

const require = createRequire(import.meta.url);
const scriptPath = resolve(process.cwd(), "scripts/stable-unit-suite.js");

const loadSuite = () => require(scriptPath);

describe("stable-unit-suite", () => {
  it("tracks a Vitest-native stable subset only", () => {
    const { STABLE_UNIT_TEST_FILES } = loadSuite();

    expect(STABLE_UNIT_TEST_FILES.length).toBeGreaterThan(5);
    expect(STABLE_UNIT_TEST_FILES).toContain("tests/unit/config/pageConfig.test.ts");
    expect(STABLE_UNIT_TEST_FILES).toContain("tests/unit/config/lighthouse-mainline-gates.spec.ts");
    expect(STABLE_UNIT_TEST_FILES).toContain("tests/unit/config/vitest-msw-gates.spec.ts");
    expect(STABLE_UNIT_TEST_FILES).toContain("tests/unit/config/testing-mainline-gates.spec.ts");
    expect(STABLE_UNIT_TEST_FILES).toContain("tests/unit/config/visual-chart-gates.spec.ts");
    expect(STABLE_UNIT_TEST_FILES).toContain("tests/unit/components/CommandPalette.test.ts");
    expect(STABLE_UNIT_TEST_FILES).toContain("tests/unit/layout/BaseLayout.test.ts");
    expect(STABLE_UNIT_TEST_FILES).toContain("tests/unit/layout/DomainLayouts.test.ts");
    expect(STABLE_UNIT_TEST_FILES).toContain("tests/unit/port-config-consistency.spec.ts");
    expect(STABLE_UNIT_TEST_FILES).toContain("tests/unit/AStockFeatures.spec.ts");
    expect(STABLE_UNIT_TEST_FILES).toContain("tests/unit/ChartInteraction.spec.ts");
    expect(STABLE_UNIT_TEST_FILES).toContain("tests/unit/use-strategy.spec.ts");
    expect(STABLE_UNIT_TEST_FILES).toContain("tests/unit/utils/indicators.test.ts");
    expect(STABLE_UNIT_TEST_FILES).toContain("tests/unit/kline-chart.spec.ts");
    expect(STABLE_UNIT_TEST_FILES).toContain("src/api/adapters/marketAdapter.spec.ts");
    expect(STABLE_UNIT_TEST_FILES).toContain("src/api/__tests__/strategy.test.ts");
    expect(STABLE_UNIT_TEST_FILES).toContain("src/api/services/__tests__/dashboardService.spec.ts");
    expect(STABLE_UNIT_TEST_FILES).toContain("src/api/services/__tests__/strategyService.msw.spec.ts");
    expect(STABLE_UNIT_TEST_FILES).toContain("src/api/__tests__/unifiedApiClient.contract.test.ts");
    expect(STABLE_UNIT_TEST_FILES).toContain("src/stores/__tests__/auth-guard.spec.ts");
    expect(STABLE_UNIT_TEST_FILES).toContain("tests/unit/scripts/validate-e2e-setup.spec.ts");
    expect(STABLE_UNIT_TEST_FILES.some((file: string) => file.includes("__node_tests__"))).toBe(false);
  });

  it("builds a direct vitest run command from the stable subset", () => {
    const { buildStableVitestArgs } = loadSuite();

    expect(buildStableVitestArgs()[0]).toBe("run");
    expect(buildStableVitestArgs()).toContain("tests/unit/structure.test.ts");
  });
});
