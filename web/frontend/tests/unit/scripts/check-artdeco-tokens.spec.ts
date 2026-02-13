import { describe, expect, it } from "vitest";
import {
  analyzeContent,
  extractStyleBlocks,
} from "../../../scripts/check-artdeco-tokens.js";

describe("check-artdeco-tokens", () => {
  it("flags duplicate custom properties and ignores comments", () => {
    const css = `
:root {
  --artdeco-gold-primary: #D4AF37;
  /* --artdeco-gold-primary: #111111; */
  --artdeco-gold-primary: #C89C2C;
}
`;

    const result = analyzeContent(css, {
      strict: true,
      literalAllowList: ["1px"],
      filePath: "src/styles/sample.scss",
    });

    expect(result.errors.join("\n")).toContain("duplicate custom property");
  });

  it("parses only style blocks for vue files", () => {
    const vue = `
<template>
  <div style="color: #FFFFFF">token-like --artdeco-fake: #000000</div>
</template>
<script setup lang="ts">
const fake = "--artdeco-script-dup: #111111";
</script>
<style scoped>
.card {
  color: var(--artdeco-gold-primary);
  border: 1px solid var(--artdeco-border-default);
}
</style>
`;

    const styles = extractStyleBlocks(vue, "src/components/FakeCard.vue");
    expect(styles).toHaveLength(1);

    const result = analyzeContent(styles[0], {
      strict: true,
      literalAllowList: ["1px"],
      filePath: "src/components/FakeCard.vue",
    });

    expect(result.errors).toEqual([]);
  });
});
