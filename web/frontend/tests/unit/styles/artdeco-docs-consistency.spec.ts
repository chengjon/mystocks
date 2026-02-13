import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

const repoRoot = resolve(process.cwd(), "..", "..");

const readDoc = (relativePath: string) =>
  readFileSync(resolve(repoRoot, relativePath), "utf8");

describe("artdeco docs consistency", () => {
  it("uses v3 governance language consistently", () => {
    const indexText = readDoc("docs/guides/ARTDECO_MASTER_INDEX.md");
    const catalogText = readDoc("web/frontend/ARTDECO_COMPONENTS_CATALOG.md");
    const architectureText = readDoc(
      "docs/api/ArtDeco_System_Architecture_Summary.md",
    );
    const guideText = readDoc("docs/guides/ARTDECO_COMPONENT_GUIDE.md");

    expect(indexText).toContain("ArtDeco v3/v3.1 Governance Baseline");
    expect(indexText).not.toContain("v2.0 Design System");
    expect(indexText).toContain("历史/归档");

    expect(catalogText).toContain("V3.1 Governance Baseline");
    expect(architectureText).toContain("V3.1 Governance Baseline");
    expect(guideText).toContain("V3.1 Governance Baseline");
  });
});
