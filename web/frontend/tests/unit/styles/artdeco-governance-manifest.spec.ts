import { describe, expect, it } from "vitest";
import manifest from "@/styles/artdeco-governance-manifest.json";

describe("artdeco governance manifest", () => {
  it("contains required sections", () => {
    expect(manifest.tokens).toBeDefined();
    expect(manifest.typography).toBeDefined();
    expect(manifest.spacing).toBeDefined();
    expect(manifest.docs).toBeDefined();
  });

  it("contains baseline governance fields", () => {
    expect(manifest.tokens.version).toBe("v3.1");
    expect(manifest.tokens.requiredVariables).toContain("--artdeco-bg-global");
    expect(manifest.tokens.requiredVariables).toContain("--artdeco-gold-primary");
    expect(manifest.typography.families).toEqual([
      "Cinzel",
      "Barlow",
      "JetBrains Mono",
    ]);
    expect(manifest.spacing.levels).toHaveLength(11);
    expect(manifest.docs.corePaths).toEqual(
      expect.arrayContaining([
        "docs/guides/ARTDECO_MASTER_INDEX.md",
        "docs/guides/ARTDECO_COMPONENT_GUIDE.md",
        "docs/api/ArtDeco_System_Architecture_Summary.md",
        "web/frontend/ARTDECO_COMPONENTS_CATALOG.md",
      ]),
    );
  });
});
