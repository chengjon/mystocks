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

  it("runs the full frontend unit suite as a blocking frontend-testing gate", () => {
    const workflowText = readWorkflow(".github/workflows/frontend-testing.yml");
    const stableUnitStepMatch = workflowText.match(
      /- name: Run stable unit tests[\s\S]*?run:\s*([^\n]+)/u,
    );
    const unitTestStepMatch = workflowText.match(
      /- name: Run full unit tests[\s\S]*?run:\s*([^\n]+)/u,
    );

    expect(stableUnitStepMatch?.[1]?.trim()).toBe("npm run test:unit:stable");
    expect(unitTestStepMatch?.[1]?.trim()).toBe("npm run test");
    expect(workflowText).not.toMatch(
      /- name: Run full unit tests[\s\S]*?continue-on-error:\s*true/u,
    );
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

  it("keeps the legacy e2e-testing workflow aligned with the Lighthouse mainline", () => {
    const workflowText = readWorkflow(".github/workflows/e2e-testing.yml");

    expect(workflowText).toContain("npm run test:e2e:lighthouse");
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

  it("treats tsc and eslint diagnostics as zero-error gates in the TypeScript workflow", () => {
    const typeWorkflowText = readWorkflow(".github/workflows/typescript-type-check.yml");

    expect(typeWorkflowText).toContain('if [ -f tsc-results/tsc-output.txt ]');
    expect(typeWorkflowText).toContain('TSC_ERROR_COUNT=$(grep -c "error TS" tsc-results/tsc-output.txt');
    expect(typeWorkflowText).toContain('if [ "$ESLINT_COUNT" -gt 0 ]');
    expect(typeWorkflowText).not.toContain('if [ "$ESLINT_COUNT" -gt 100 ]');
  });

  it("keeps the long-term frontend type debt baseline aligned with the zero-error gate", () => {
    const baseline = readJson<{ frontend_type_errors: number }>(
      "reports/analysis/tech-debt-baseline.json",
    );

    expect(baseline.frontend_type_errors).toBe(0);
  });
});
