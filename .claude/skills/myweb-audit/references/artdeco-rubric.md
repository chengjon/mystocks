# ArtDeco Rubric

> **权威来源声明**:
> 本文件是专题说明或状态说明，不是仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先阅读 `architecture/STANDARDS.md`；若涉及执行入口、提案流程或当前实现事实，再分别参考根目录 `AGENTS.md`、根目录 `CLAUDE.md`、`openspec/AGENTS.md` 与当前代码。

Use this rubric to evaluate whether a page fits the project's ArtDeco direction.

## Core Principles

The page should express the repository's current ArtDeco identity:

- `Original ArtDeco + A-share financial semantics + high-density quant workbench`
- data-first, not decoration-first
- strong structure, restrained ornament
- clear hierarchy with deliberate heading treatment
- elegant readability under dense information

This is not a generic luxury style. It is a structured fintech workbench style.

Use current repository truth when judging:

- headings should align with the ArtDeco title language
- body text should remain practical and readable
- numeric/meta content should use the repo's existing mono-oriented treatment where appropriate
- rise/profit must remain red, down/loss must remain green
- tables, quotes, pnl metrics, signals, and chart surfaces must preserve financial readability before ornament

## 1. Geometry and Boundaries

Expect:

- clear block boundaries
- visible section separation
- stable axes and alignment
- intentional rectangular structure
- adherence to the existing grid and container rhythm used by the page family

Flag issues when:

- blocks bleed into each other
- card boundaries are vague
- layout feels soft, loose, or shapeless
- decorative treatment replaces structure
- grid rhythm collapses into arbitrary spacing

Observable checks:

- sections have clear framing or separation
- boundaries are defined by structure, border, or disciplined spacing
- cards and panels do not visually dissolve into each other
- shared workbench containers keep a stable internal grid

Common failure signs:

- sections blend together without rank
- arbitrary spacing is used instead of structural grouping
- cards rely on shadow only, with weak framing

## 2. Vertical Rhythm and Hierarchy

Expect:

- a clear top-down reading rhythm
- strong section titles or title bands
- obvious hierarchy between page title, section title, body text, and metadata
- consistent spacing steps between levels

Flag issues when:

- all text weights feel similar
- sections blend together
- title areas feel generic or weak
- spacing does not express hierarchy

Observable checks:

- page title, section title, module title, body text, and metadata are visibly distinct
- title treatment feels deliberate rather than default
- spacing steps reflect content rank
- dense pages still preserve reading order

Common failure signs:

- every text block looks equally important
- headings are visually weak or inconsistent
- metadata and primary content compete for attention

Use the existing repository type scale and token patterns for judgment. Do not invent a new pixel-based hierarchy in this skill.

## 3. Decorative Restraint

Expect:

- restrained divider lines, border accents, or framing devices
- structural decoration that reinforces hierarchy
- consistent treatment of cards, panels, and headings

Flag issues when:

- decoration is random or overused
- gradients dominate instead of structure
- shadows are used to fake hierarchy
- ornament competes with data

Observable checks:

- ornament reinforces structure instead of competing with data
- border accents, dividers, and framing devices are sparse and repeatable
- current reduced brand chrome remains respected

Common failure signs:

- decoration feels pasted on
- glow, gradients, or lines dominate the page
- old decorative chrome is reintroduced without structural purpose

## 4. Color Discipline

Expect:

- restrained ArtDeco fintech palette
- token-aligned color usage
- A-share semantics preserved:
  - rise/profit = red
  - down/loss = green
- contrast supports dense financial data reading

Also check:

- no local color drift when shared tokens exist
- glow usage follows financial meaning and stays restrained
- chips, badges, overlays, and status surfaces prefer existing shared component semantics

Common failure signs:

- local hardcoded colors bypass token systems
- profit/loss semantics are reversed or diluted
- too many accent colors weaken information hierarchy

Do not define new allowed or forbidden hex values here. Defer to existing tokens and shared styles.

## 5. Cards, Tables, and Charts

Expect:

- clear dominance relationships between modules
- cards with intentional framing
- tables that look structured rather than flat
- charts sized according to importance, not convenience
- dense information presented with elegance and calm

Flag issues when:

- every module looks equally important
- table headers are weak or visually detached
- charts are too short, cramped, or oversized without purpose
- card padding and borders feel arbitrary

Observable checks:

- cards use intentional framing and stable padding
- table headers feel anchored and structured
- chart height and prominence match page importance
- numeric blocks use strong alignment and readable density
- shared components such as badge, button, card, loading, and status patterns are reused where appropriate
- tabular numeric values align consistently within their columns
- financial data remains readable under high density

Common failure signs:

- table headers feel detached
- chart areas are cramped or oversized without reason
- cards drift from shared component behavior and token rhythm
- values with similar meaning do not align consistently

Use repository truth for concrete table styles, density, spacing, and token application. Do not define new low-level table measurements here.

## 6. Disallowed Patterns

Treat these as anti-patterns unless the page already has a strong system-approved reason:

- cheap multi-color gradients
- overly rounded corners without structural reason
- excessive shadow stacking
- decorative noise not tied to hierarchy
- playful UI effects that weaken authority
- weak heading treatment on high-density pages

Limited exceptions are acceptable only when the page is a clearly defined special-purpose view already aligned with repository standards. Even then, exceptions must not break token discipline, financial semantics, or page-family consistency.

Do not define new hard thresholds for gradient styles or radius values here. Judge them against the current repository system and page-family norms.

## 7. Page-Type Weighting

Apply the rubric with different strictness by page role:

- core trading, risk, strategy, and dashboard pages:
  strict ArtDeco compliance expected
- dense detail and analysis pages:
  structure and hierarchy remain strict, ornament may stay lighter
- auxiliary settings or utility pages:
  visual language must remain consistent, but decoration can be reduced

Do not use this weighting to justify generic admin styling on core business pages.

## Quick Pass / Fail Heuristics

A page is likely non-compliant if:

- it looks like a generic admin panel with no structural identity
- it relies on color and shadow instead of border and hierarchy
- it feels visually soft, loose, or casual
- high-density information becomes chaotic instead of composed

A page is closer to compliant if:

- modules are framed and ordered clearly
- titles feel deliberate
- spacing and borders express rank and grouping
- the page reads as disciplined, elegant, and intentional
