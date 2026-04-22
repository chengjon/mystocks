import fs from "node:fs";
import path from "node:path";
import { describe, expect, it } from "vitest";

const frontendRoot = path.resolve(__dirname, "../../..");
const repoRoot = path.resolve(frontendRoot, "..", "..");

const readWorkflow = (relativePath: string) =>
  fs.readFileSync(path.join(repoRoot, relativePath), "utf8");
const readJson = <T>(relativePath: string) =>
  JSON.parse(fs.readFileSync(path.join(repoRoot, relativePath), "utf8")) as T;

const packageJson = JSON.parse(
  fs.readFileSync(path.join(frontendRoot, "package.json"), "utf8"),
) as { scripts: Record<string, string> };

describe("CI workflow gates", () => {
  it("defines a dedicated stable unit suite command", () => {
    expect(packageJson.scripts["test:unit:stable"]).toBeDefined();
  });

  it("defines an axe-backed E2E accessibility smoke command", () => {
    expect(packageJson.scripts["test:e2e:axe"]).toBeDefined();
  });

  it("defines a Lighthouse CI smoke command", () => {
    expect(packageJson.scripts["test:e2e:lighthouse"]).toBeDefined();
  });

  it("defines ArtDeco documentation governance commands for full and changed-only checks", () => {
    expect(packageJson.scripts["lint:artdeco:guidance"]).toBeDefined();
    expect(packageJson.scripts["lint:artdeco:guidance:changed"]).toBeDefined();
    expect(packageJson.scripts["lint:artdeco:changed"]).toBeDefined();
    expect(packageJson.scripts["lint:artdeco:changed"]).toContain("--target-dir src/layouts");
    expect(packageJson.scripts["lint:artdeco:changed"]).toContain("--target-dir src/components/layout");
    expect(packageJson.scripts["lint:artdeco:changed"]).toContain("--target-dir src/components/menu");
    expect(packageJson.scripts["lint:artdeco:changed"]).toContain("--target-dir src/components/common");
    expect(packageJson.scripts["lint:artdeco:changed"]).toContain("--target-dir src/views/styles");
    expect(packageJson.scripts["lint:artdeco:changed"]).toContain("--target-dir src/components/shared/ui");
    expect(packageJson.scripts["lint:artdeco:changed"]).toContain("--target-file src/views/SkeletonUsage.vue");
    expect(packageJson.scripts["lint:artdeco:changed"]).toContain("--target-file src/views/Stocks.vue");
  });

  it("defines visual regression package scripts for workflow reuse", () => {
    expect(packageJson.scripts["test:visual"]).toBeDefined();
    expect(packageJson.scripts["test:visual:update"]).toBeDefined();
    expect(packageJson.scripts["test:visual:dashboard"]).toBeDefined();
    expect(packageJson.scripts["test:visual:dashboard:update"]).toBeDefined();
    expect(packageJson.scripts["test:visual:charts"]).toBeDefined();
    expect(packageJson.scripts["test:visual:charts:update"]).toBeDefined();
  });

  it("defines a blocking Chromium business-smoke command", () => {
    expect(packageJson.scripts["test:e2e:business-smoke"]).toBeDefined();
    expect(packageJson.scripts["test:e2e:auth"]).toBeDefined();
  });

  it("runs the full frontend unit suite as a blocking frontend-testing gate", () => {
    const workflowText = readWorkflow(".github/workflows/frontend-testing.yml");
    const frontendTestSection = workflowText.split("frontend-test:")[1]?.split("frontend-security:")[0];
    const stableUnitStepMatch = frontendTestSection.match(
      /- name: Run stable unit tests[\s\S]*?run:\s*([^\n]+)/u,
    );
    const unitTestStepMatch = frontendTestSection.match(
      /- name: Run full unit tests[\s\S]*?run:\s*([^\n]+)/u,
    );

    expect(stableUnitStepMatch?.[1]?.trim()).toBe("npm run test:unit:stable");
    expect(unitTestStepMatch?.[1]?.trim()).toBe("npm run test");
    expect(frontendTestSection).not.toMatch(
      /- name: Run full unit tests[\s\S]*?continue-on-error:\s*true/u,
    );
  });

  it("runs the Chromium business-smoke suite in frontend-testing", () => {
    const workflowText = readWorkflow(".github/workflows/frontend-testing.yml");
    const e2eStepMatch = workflowText.match(/- name: Run business smoke e2e tests[\s\S]*?npm run test:e2e:stable/u);

    expect(e2eStepMatch?.[0]).toContain("npm run test:e2e:stable");
  });

  it("runs the axe accessibility smoke in frontend-testing", () => {
    const workflowText = readWorkflow(".github/workflows/frontend-testing.yml");
    const axeStepMatch = workflowText.match(
      /- name: Run axe accessibility smoke[\s\S]*?run:\s*([^\n]+)/u,
    );

    expect(axeStepMatch?.[1]?.trim()).toBe("npm run test:e2e:axe");
  });

  it("runs Lighthouse CI smoke in frontend-testing", () => {
    const workflowText = readWorkflow(".github/workflows/frontend-testing.yml");
    const lighthouseStepMatch = workflowText.match(
      /- name: Run Lighthouse CI smoke[\s\S]*?run:\s*([^\n]+)/u,
    );

    expect(lighthouseStepMatch?.[1]?.trim()).toBe("npm run test:e2e:lighthouse");
  });

  it("runs the PM2 API performance baseline in the route/layout runtime job", () => {
    const workflowText = readWorkflow(".github/workflows/frontend-testing.yml");
    const runtimeBaselineStepMatch = workflowText.match(
      /- name: Run route\/layout runtime baseline[\s\S]*?run:\s*([^\n]+)/u,
    );

    expect(runtimeBaselineStepMatch?.[1]?.trim()).toBe("bash scripts/run_frontend_runtime_baseline.sh");
    expect(workflowText).toContain("route-layout-api-performance-baseline");
    expect(workflowText).toContain("tests/performance/benchmark.py");
    expect(workflowText).toContain("tests/performance/api_smoke_endpoints.json");
    expect(workflowText).not.toContain("- name: Run PM2 API performance baseline");
  });

  it("runs the PM2 monitoring auth performance baseline in the route/layout runtime job", () => {
    const workflowText = readWorkflow(".github/workflows/frontend-testing.yml");
    expect(workflowText).toContain("route-layout-monitoring-auth-performance-baseline");
    expect(workflowText).toContain("tests/performance/monitoring_auth_endpoints.json");
    expect(workflowText).toContain("scripts/run_monitoring_auth_performance_baseline.sh");
    expect(workflowText).not.toContain("- name: Run PM2 monitoring auth performance baseline");
  });

  it("runs the unified runtime quality summary in the route/layout runtime job", () => {
    const workflowText = readWorkflow(".github/workflows/frontend-testing.yml");
    expect(workflowText).toContain("route-layout-runtime-quality-summary");
    expect(workflowText).toContain("scripts/dev/quality_gate/build_runtime_quality_summary.py");
    expect(workflowText).toContain("tests/performance/test_build_runtime_quality_summary.py");
    expect(workflowText).not.toContain("- name: Run unified runtime quality summary");
  });

  it("uploads a consolidated runtime artifact bundle with a manifest", () => {
    const workflowText = readWorkflow(".github/workflows/frontend-testing.yml");

    expect(workflowText).toContain("Build consolidated runtime artifact manifest");
    expect(workflowText).toContain("scripts/dev/quality_gate/build_runtime_ci_bundle.py");
    expect(workflowText).toContain("reports/analysis/runtime-ci-bundle/runtime-artifact-manifest.json");
    expect(workflowText).toContain("reports/analysis/runtime-ci-bundle/runtime-artifact-index.md");
    expect(workflowText).toContain("route-layout-runtime-bundle");
    expect(workflowText).toContain("${{ env.REPORT_DIR }}");
    expect(workflowText).toContain("${{ env.API_REPORT_DIR }}");
    expect(workflowText).toContain("${{ env.MONITORING_API_REPORT_DIR }}");
    expect(workflowText).toContain("${{ env.RUNTIME_QUALITY_REPORT_DIR }}");
  });

  it("runs a dedicated containerized runtime smoke job on container-scope changes", () => {
    const workflowText = readWorkflow(".github/workflows/frontend-testing.yml");

    expect(workflowText).toContain("container_runtime_required");
    expect(workflowText).toContain("scripts/run_containerized_runtime_smoke.sh");
    expect(workflowText).toContain("name: Containerized Runtime Smoke");
    expect(workflowText).toContain("containerized-runtime-smoke");
    expect(workflowText).toContain("containerized-runtime-bundle");
    expect(workflowText).toContain("DOCKER_REPORT_DIR");
  });

  it("builds a downstream runtime delivery summary from PM2 and Docker artifacts", () => {
    const workflowText = readWorkflow(".github/workflows/frontend-testing.yml");

    expect(workflowText).toContain("name: Runtime Delivery Summary");
    expect(workflowText).toContain("Validate runtime delivery prerequisites");
    expect(workflowText).toContain("actions/download-artifact@v4");
    expect(workflowText).toContain("route-layout-runtime-baseline");
    expect(workflowText).toContain("route-layout-api-performance-baseline");
    expect(workflowText).toContain("route-layout-monitoring-auth-performance-baseline");
    expect(workflowText).toContain("containerized-runtime-smoke");
    expect(workflowText).toContain("build_runtime_quality_summary.py");
    expect(workflowText).toContain("Validate runtime observability drift");
    expect(workflowText).toContain("Rebuild combined runtime quality summary with drift report");
    expect(workflowText).toContain("validate_runtime_observability_drift.py");
    expect(workflowText).toContain("runtime-observability-baseline.json");
    expect(workflowText).toContain("runtime-observability-drift-report.json");
    expect(workflowText).toContain("--docker-dir");
    expect(workflowText).toContain("needs.route-layout-pm2-detect.outputs.gate_required == 'true' || needs.frontend-gate-scope-detect.outputs.container_runtime_required == 'true'");
    expect(workflowText).toContain("runtime-delivery-summary");
    expect(workflowText).toContain("runtime-delivery-bundle");

    const firstBuildIndex = workflowText.indexOf("Build combined runtime quality summary");
    const driftIndex = workflowText.indexOf("Validate runtime observability drift");
    const rebuildIndex = workflowText.indexOf("Rebuild combined runtime quality summary with drift report");
    expect(firstBuildIndex).toBeGreaterThan(-1);
    expect(driftIndex).toBeGreaterThan(firstBuildIndex);
    expect(rebuildIndex).toBeGreaterThan(driftIndex);
  });

  it("builds a human-readable runtime artifact index in the consolidated bundle", () => {
    const workflowText = readWorkflow(".github/workflows/frontend-testing.yml");
    const bundleScriptText = readWorkflow("scripts/dev/quality_gate/build_runtime_ci_bundle.py");

    expect(workflowText).toContain("runtime-artifact-index.md");
    expect(workflowText).toContain("scripts/dev/quality_gate/build_runtime_ci_bundle.py");
    expect(workflowText).toContain("--runtime-observability-drift-report");
    expect(bundleScriptText).toContain("# Runtime Artifact Index");
    expect(bundleScriptText).toContain("## Key Gates");
    expect(bundleScriptText).toContain("## Report Entry Points");
    expect(bundleScriptText).toContain("## Performance Snapshot");
    expect(bundleScriptText).toContain("## Drift Gate");
    expect(bundleScriptText).toContain("docker_runtime");
    expect(bundleScriptText).toContain("Docker runtime smoke");
  });

  it("publishes the runtime artifact index into the GitHub Actions job summary", () => {
    const workflowText = readWorkflow(".github/workflows/frontend-testing.yml");

    expect(workflowText).toContain("Publish runtime artifact summary to GitHub Actions job summary");
    expect(workflowText).toContain("GITHUB_STEP_SUMMARY");
    expect(workflowText).toContain('cat reports/analysis/runtime-ci-bundle/runtime-artifact-index.md >> "$GITHUB_STEP_SUMMARY"');
  });

  it("runs the changed-only ArtDeco guidance gate in frontend-testing", () => {
    const workflowText = readWorkflow(".github/workflows/frontend-testing.yml");
    const guidanceStepMatch = workflowText.match(
      /- name: Run ArtDeco guidance changed-file gate[\s\S]*?run:\s*([^\n]+)/u,
    );

    expect(guidanceStepMatch?.[1]?.trim()).toBe("npm run lint:artdeco:guidance:changed");
  });

  it("runs the changed-only ArtDeco source gate in frontend-testing", () => {
    const workflowText = readWorkflow(".github/workflows/frontend-testing.yml");
    const sourceStepMatch = workflowText.match(
      /- name: Run ArtDeco token changed-file gate[\s\S]*?run:\s*([^\n]+)/u,
    );

    expect(sourceStepMatch?.[1]?.trim()).toBe("npm run lint:artdeco:changed");
  });

  it("treats ArtDeco components as ArtDeco scope inputs during workflow detection", () => {
    const workflowText = readWorkflow(".github/workflows/frontend-testing.yml");

    expect(workflowText).toContain("web/frontend/src/components/artdeco/*");
    expect(workflowText).toContain("web/frontend/src/components/artdeco/**");
    expect(workflowText).toContain("web/frontend/src/layouts/*");
    expect(workflowText).toContain("web/frontend/src/layouts/**");
    expect(workflowText).toContain("web/frontend/src/components/layout/*");
    expect(workflowText).toContain("web/frontend/src/components/layout/**");
    expect(workflowText).toContain("web/frontend/src/components/menu/*");
    expect(workflowText).toContain("web/frontend/src/components/menu/**");
    expect(workflowText).toContain("web/frontend/src/components/common/*");
    expect(workflowText).toContain("web/frontend/src/components/common/**");
    expect(workflowText).toContain("web/frontend/src/views/styles/*");
    expect(workflowText).toContain("web/frontend/src/views/styles/**");
    expect(workflowText).toContain("web/frontend/src/components/shared/ui/*");
    expect(workflowText).toContain("web/frontend/src/components/shared/ui/**");
    expect(workflowText).toContain("web/frontend/src/views/SkeletonUsage.vue");
    expect(workflowText).toContain("web/frontend/src/views/Stocks.vue");
  });

  it("keeps the dedicated cross-browser workflow aligned with the Playwright mainline", () => {
    const workflowText = readWorkflow(".github/workflows/e2e-testing.yml");

    expect(workflowText).toContain("npm run test:e2e:lighthouse");
    expect(workflowText).toContain("tests/e2e/auth-login.spec.ts");
    expect(workflowText).toContain("tests/e2e/critical/menu-navigation-fixed.spec.ts");
    expect(workflowText).toContain("tests/e2e/kline-chart.spec.ts");
    expect(workflowText).not.toContain(".lighthouserc.json");
  });

  it("aligns the standalone Playwright workflow with the standard stable E2E entrypoint", () => {
    const workflowText = readWorkflow(".github/workflows/playwright.yml");

    expect(workflowText).toContain("working-directory: web/frontend");
    expect(workflowText).toContain("npm run test:e2e:stable");
    expect(workflowText).not.toContain("playwright.config.ts");
  });

  it("enforces a zero type error ceiling in the frontend and TypeScript workflows", () => {
    const frontendWorkflowText = readWorkflow(".github/workflows/frontend-testing.yml");
    const typeWorkflowText = readWorkflow(".github/workflows/typescript-type-check.yml");

    expect(frontendWorkflowText).toContain("TYPE_ERROR_CEILING: '0'");
    expect(typeWorkflowText).toContain("TYPE_ERROR_CEILING: '0'");
    expect(typeWorkflowText).toContain("node scripts/check-type-error-ceiling.js");
    expect(typeWorkflowText).not.toContain("Filter type errors");
    expect(typeWorkflowText).not.toContain("vue-tsc-filtered.txt");
  });

  it("defines a scheduled weekly governance workflow that runs the stable wrapper", () => {
    const workflowText = readWorkflow(".github/workflows/tech-debt-weekly-governance.yml");

    expect(workflowText).toContain("name: Tech Debt Weekly Governance");
    expect(workflowText).toContain("schedule:");
    expect(workflowText).toContain("workflow_dispatch:");
    expect(workflowText).toContain("Generate Weekly Governance Report");
    expect(workflowText).toContain("Run full runtime delivery gate");
    expect(workflowText).toContain("bash scripts/run_full_runtime_delivery_gate.sh");
    expect(workflowText).toContain("RUNTIME_DELIVERY_GATE_DIR");
    expect(workflowText).toContain("bash scripts/run_tech_debt_weekly_report.sh");
    expect(workflowText).toContain("tech-debt-weekly-governance-report");
    expect(workflowText).toContain("runtime-delivery-gate-weekly");
    expect(workflowText).toContain("GITHUB_STEP_SUMMARY");
    expect(workflowText).toContain("## Debt KPI");
    expect(workflowText).toContain("## Runtime KPI");
    expect(workflowText).toContain("## Current Batch");
    expect(workflowText).toContain('"- new_debt_violations:"');
    expect(workflowText).toContain('"- Runtime drift gate:"');
    expect(workflowText).toContain('line.startswith("- Current batch issue:")');
    expect(workflowText).toContain('line.startswith("- Current batch introduced issues:")');
    expect(workflowText).not.toContain("for line in lines[:30]");
  });

  it("defines a scheduled runtime delivery gate workflow that runs the full wrapper", () => {
    const workflowText = readWorkflow(".github/workflows/runtime-delivery-gate.yml");

    expect(workflowText).toContain("name: Runtime Delivery Gate");
    expect(workflowText).toContain("schedule:");
    expect(workflowText).toContain("workflow_dispatch:");
    expect(workflowText).toContain("Run Full Runtime Delivery Gate");
    expect(workflowText).toContain("bash scripts/run_full_runtime_delivery_gate.sh");
    expect(workflowText).toContain("POSTGRES_PASSWORD=postgres");
    expect(workflowText).toContain("TDENGINE_PASSWORD=taosdata");
    expect(workflowText).toContain("runtime-delivery-gate-ci");
    expect(workflowText).toContain("runtime-delivery-gate");
    expect(workflowText).toContain("GITHUB_STEP_SUMMARY");
    expect(workflowText).toContain('cat reports/analysis/runtime-delivery-gate-ci/SUMMARY.md >> "$GITHUB_STEP_SUMMARY"');
    expect(workflowText).toContain('cat reports/analysis/runtime-delivery-gate-ci/runtime-quality-summary/SUMMARY.md >> "$GITHUB_STEP_SUMMARY"');
  });

  it("treats tsc and eslint diagnostics as zero-error gates in the TypeScript workflow", () => {
    const typeWorkflowText = readWorkflow(".github/workflows/typescript-type-check.yml");

    expect(typeWorkflowText).toContain('if [ -f type-check-artifacts/tsc-results/tsc-output.txt ]');
    expect(typeWorkflowText).toContain('TSC_ERROR_COUNT=$(grep -c "error TS" type-check-artifacts/tsc-results/tsc-output.txt');
    expect(typeWorkflowText).toContain('ARTIFACT_DIR="${{ github.workspace }}/type-check-artifacts/tsc-results"');
    expect(typeWorkflowText).toContain('path: type-check-artifacts');
    expect(typeWorkflowText).toContain('if [ "$ESLINT_COUNT" -gt 0 ]');
    expect(typeWorkflowText).not.toContain('if [ "$ESLINT_COUNT" -gt 100 ]');
  });

  it("keeps the long-term frontend type debt baseline aligned with the zero-error gate", () => {
    const baseline = readJson<{ frontend_type_errors: number }>(
      "reports/analysis/tech-debt-baseline.json",
    );

    expect(baseline.frontend_type_errors).toBe(0);
  });

  it("watches the real frontend visual test tree in the visual workflow", () => {
    const workflowText = readWorkflow(".github/workflows/visual-testing.yml");

    expect(workflowText).toContain("web/frontend/tests/visual/**");
    expect(workflowText).not.toContain("'tests/visual/**'");
  });

  it("uses package scripts instead of inline playwright commands in the visual workflow", () => {
    const workflowText = readWorkflow(".github/workflows/visual-testing.yml");

    expect(workflowText).toContain("npm run test:visual:dashboard --");
    expect(workflowText).toContain("npm run test:visual:charts --");
    expect(workflowText).toContain("npm run test:visual:dashboard:update");
    expect(workflowText).toContain("npm run test:visual:charts:update");
    expect(workflowText).toContain("VISUAL_HTML_REPORT_DIR=playwright-report/dashboard");
    expect(workflowText).toContain("VISUAL_HTML_REPORT_DIR=playwright-report/charts");
    expect(workflowText).toContain("visual-dashboard-results-${{ matrix.browser }}");
    expect(workflowText).toContain("visual-chart-results-${{ matrix.browser }}");
    expect(workflowText).not.toContain("npx playwright test \\");
  });

  it("writes a grouped visual summary for dashboard and chart suites", () => {
    const workflowText = readWorkflow(".github/workflows/visual-testing.yml");

    expect(workflowText).toContain("visual-test-summary.json");
    expect(workflowText).toContain("dashboard_tests");
    expect(workflowText).toContain("dashboard_passed");
    expect(workflowText).toContain("chart_tests");
    expect(workflowText).toContain("chart_passed");
  });
});
