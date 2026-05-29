# ArtDeco Critique: `risk/Alerts.vue`

Date: 2026-05-29

Status: critique only, awaiting shape decision

Target: `web/frontend/src/views/risk/Alerts.vue`

Command intent: `$impeccable critique web/frontend/src/views/risk/Alerts.vue`

## 1. Scope and Method

This critique reviews the currently implemented Web ArtDeco design for the risk alerts route. It does not approve implementation changes.

Evidence used:

- Route truth: `web/frontend/src/router/index.ts` maps `/risk/alerts` to `@/views/risk/Alerts.vue`.
- Source review: `web/frontend/src/views/risk/Alerts.vue`.
- Embedded panel review: `web/frontend/src/views/risk/AlertRuleManagementPanel.vue`.
- Product register: `product`, desktop Web, A-share quantitative analysis terminal.
- ArtDeco posture: data-first, restrained, authoritative, tokenized, operational.
- Automated detector: `npx impeccable --json web/frontend/src/views/risk/Alerts.vue`.

Browser overlay review was not run because browser automation tools were not available in this session. Sub-agent isolation was not used because the available sub-agent tool requires explicit user authorization for delegation; this report uses sequential fallback assessment.

## 2. Route and Ownership

Route status: active routed page.

Router evidence:

- `/risk` redirects to `/risk/overview`.
- `risk-alerts` uses `component: () => import('@/views/risk/Alerts.vue')`.

Ownership classification:

- Canonical route page: `web/frontend/src/views/risk/Alerts.vue`.
- Embedded supporting panel: `web/frontend/src/views/risk/AlertRuleManagementPanel.vue`.
- Not a legacy `views/artdeco-pages/**` wrapper.

This makes `risk/Alerts.vue` a valid next candidate after the `market/Realtime.vue` pilot.

## 3. Design Health Score

| # | Heuristic | Score | Key Issue |
|---|---:|---:|---|
| 1 | Visibility of System Status | 3 | Header status, loading, and runtime messages exist, but data age, degraded state, and recovery hierarchy are not explicit enough |
| 2 | Match System / Real World | 3 | Risk language is mostly useful, but English scaffolding such as `alert governance desk` and `alert review route` feels internal |
| 3 | User Control and Freedom | 2 | Refresh and modal close/cancel exist, but alert review lacks clear triage controls, filters, bulk actions, and reset paths |
| 4 | Consistency and Standards | 2 | ArtDeco components, Element Plus table, native inline buttons, duplicated stat areas, and modal-like rule editing create mixed vocabulary |
| 5 | Error Prevention | 2 | Rule deletion appears guarded, but alert triage and rule mutation risk are not visually separated or staged |
| 6 | Recognition Rather Than Recall | 2 | Counts are visible, but the user has to infer what to do next with unread or high-priority alerts |
| 7 | Flexibility and Efficiency | 1 | No visible severity filter, unread filter, bulk handling, keyboard path, or fast triage workflow |
| 8 | Aesthetic and Minimalist Design | 2 | The page is card-heavy and repeats metrics before the alert table becomes useful |
| 9 | Error Recovery | 2 | Stale snapshot messages exist, but recovery is mostly "refresh again"; no structured degraded-state strip |
| 10 | Help and Documentation | 1 | No contextual explanation for alert levels, rule behavior, or stale snapshot meaning |
| **Total** |  | **22/40** | **Acceptable foundation; significant design improvements needed** |

## 4. Anti-Patterns Verdict

### LLM Assessment

This page does not read as generic AI slop in the obvious sense. It uses project ArtDeco components, tokenized values, domain-specific Chinese labels, and runtime-state logic.

The risk is different: it reads like an ArtDeco wrapper around two competing tools rather than a mature risk-alert workbench. The page currently has:

- a hero/status shell,
- a top stat strip,
- a content shell,
- a second stat grid,
- a recent alerts table,
- and an embedded rule-management panel.

That structure creates a familiar "dashboard made of cards" rhythm. For this product, the user needs a focused alert review surface, not another decorative operations dashboard.

### Deterministic Scan

Command:

`npx impeccable --json web/frontend/src/views/risk/Alerts.vue`

Result:

`[]`

The detector found no built-in issue patterns. This is useful but limited: the major problems here are information architecture, operational hierarchy, and task flow, not obvious CSS slop.

### Visual Overlays

Not executed. Browser automation was unavailable in this session.

## 5. Overall Impression

The page has a solid engineering foundation: route ownership is clean, ArtDeco components are present, runtime status exists, stale snapshot handling exists, and the table/rule-panel split is understandable.

The biggest opportunity is to turn it from a status dashboard into an alert triage desk. High-priority alerts, unread state, stale data, and rule mutations should become operational controls and states, not just counts and cards.

## 6. What's Working

1. Runtime status is not an afterthought.

   `pageStatusText`, `pageStatusType`, `runtimeMessage`, verified snapshots, and stale error variables show that the page already models partial failure and stale data.

2. Route-level ArtDeco ownership is clear.

   The page imports `ArtDecoButton`, `ArtDecoCard`, `ArtDecoHeader`, `ArtDecoIcon`, and `ArtDecoStatCard` directly. It is not merely wrapped by a legacy ArtDeco page.

3. The split between alert records and alert rules is conceptually valid.

   Recent alerts and rule management are both relevant to risk governance. The issue is priority and interaction design, not the existence of both surfaces.

## 7. Priority Issues

### [P1] The page has two competing primary jobs

**What**: Alert review and rule management appear in one continuous shell. The recent alerts table and rule-management panel compete for attention, while two metric areas appear before the rule panel.

**Why it matters**: During risk review, the user first needs to know what is urgent, what changed, and what requires action. Rule configuration is a second workflow. Combining both at equal weight slows triage and makes high-severity conditions feel less urgent.

**Fix**: Shape the page as a primary alert review surface with rule management as a secondary section or explicit mode. Keep alert review above the fold: status strip, filter/control row, alert table, then rule management.

**Suggested command**: `$impeccable shape risk alerts ArtDeco triage desk`

### [P1] Runtime states exist in code but are not visually decisive

**What**: The page has `loading`, verified snapshots, stale rule/alert errors, and runtime messages. Visually, these collapse into header status, `v-loading`, empty text, and a paragraph message.

**Why it matters**: In a risk surface, stale data and partial sync are operationally different from ordinary empty results. Users must be able to distinguish live, refreshing, stale, degraded, empty, and failed states immediately.

**Fix**: Introduce a route-level status strip modeled after the Realtime pilot vocabulary. Show last verified request or freshness, partial failure scope, and a recovery action. Keep `aria-live` for message changes.

**Suggested command**: `$impeccable harden risk alerts runtime states`

### [P1] Risk severity is visible but not actionable

**What**: High-priority and unread counts exist, and table rows show `alert_level` through `el-tag`. There is no visible severity filter, unread filter, escalation grouping, or triage action.

**Why it matters**: Counting high-priority alerts is weaker than helping the user resolve them. A risk operator should not scan the full table to answer "what needs action now?"

**Fix**: Add a compact control row in the future shape brief: severity segment, unread toggle, refresh, and optional rule-mode entry. Sort or group critical/unread alerts first. Preserve A-share and Element Plus semantics where they are already stable.

**Suggested command**: `$impeccable layout risk alerts severity controls`

### [P2] The visual grammar is card-heavy and duplicates metrics

**What**: A hero shell, top stat strip, content shell, second stats grid, alert table card, and rule list card appear in one route.

**Why it matters**: The Realtime pilot established a leaner route grammar: compact header, control row, primary data area, secondary context, explicit runtime state. This page still feels like a pre-pilot ArtDeco dashboard composition.

**Fix**: Consolidate the stat surfaces. Use one status/metric band, then let the alert table own the primary area. Rule management should not force another full card hierarchy unless the user enters configuration mode.

**Suggested command**: `$impeccable distill risk alerts page grammar`

### [P2] Component vocabulary is mixed

**What**: The route uses ArtDeco components, Element Plus table, and native inline buttons in `AlertRuleManagementPanel.vue`.

**Why it matters**: Mixed button affordances make editing and deleting rules feel less governed than the rest of the page. In a risk workflow, destructive and mutating actions should be visually consistent and easy to recognize.

**Fix**: In a future implementation, align rule actions with ArtDeco button primitives or a documented inline action pattern. Keep destructive actions distinct without side-stripe decoration.

**Suggested command**: `$impeccable audit risk alerts component vocabulary`

### [P3] Internal English scaffolding weakens the product tone

**What**: Labels such as `alert governance desk`, `FOCUS: alert center`, and `alert review route` read like implementation scaffolding.

**Why it matters**: The product voice should be calm, precise, and operational. Internal English fragments add noise for a Chinese A-share terminal unless they carry a deliberate terminal convention.

**Fix**: Replace or reduce these fragments during shape. Keep request IDs and operational metadata, but phrase the page in user-facing risk language.

**Suggested command**: `$impeccable clarify risk alerts copy`

## 8. Cognitive Load Assessment

| Checklist Item | Pass/Fail | Note |
|---|---|---|
| Single focus | Fail | Alert review and rule management compete |
| Chunking | Fail | Metrics are repeated across two areas before the primary table resolves |
| Grouping | Pass | Major areas are grouped clearly |
| Visual hierarchy | Fail | Hero, metric cards, table, and rules all carry strong visual weight |
| One thing at a time | Fail | Review, monitor, configure, and mutate rules share one continuous path |
| Minimal choices | Pass | Visible action count is not excessive |
| Working memory | Pass | Counts and table remain visible together |
| Progressive disclosure | Fail | Rule management is always present rather than revealed as a secondary mode |

Failed items: 5/8.

Rating: high cognitive load for a risk triage surface.

## 9. Persona Red Flags

### Alex, Power User

- Wants to filter unread or high-priority alerts immediately, but sees only counts and a full table.
- Cannot see a bulk or fast triage path.
- Has no obvious keyboard-first path for alert review or rule edits.

### Sam, Accessibility-Dependent User

- Runtime message has `aria-live`, which is good.
- Severity is partly color/tag based; the text label helps, but future shape should ensure color is never the only signal.
- Native inline buttons inside the rule panel need consistent focus treatment and accessible labels during implementation review.

### Project-Specific Persona: A-share Risk Operator

- Needs to answer "what requires action now?" before reading full details.
- Needs to trust whether data is live, stale, or partially refreshed.
- Will lose time if rule editing visually competes with alert triage during active monitoring.

## 10. Minor Observations

- `show-overflow-tooltip` on long alert messages is useful, but the future shape should define whether the full message should be expanded inline, opened in a detail row, or left as tooltip-only.
- The page uses ArtDeco tokens heavily, which is a good base for future code work.
- Existing media queries down to `48rem` should not drive new design decisions because the product target remains desktop Web.
- The rule panel has mutation messages and empty states; those should be preserved if the panel is visually deprioritized.

## 11. Questions To Resolve Before Shape

1. Should this page optimize for alert triage first or rule management first?
2. Should unread and high-priority alerts become first-class filters in the next shape brief?
3. Should rule management stay on the page, or move behind a secondary mode such as a tab, drawer, or collapsible section?
4. Should the next implementation preserve Element Plus table behavior, or define a shared ArtDeco data-panel pattern after comparing with `market/Realtime.vue`?

## 12. Recommended Actions

Recommended next command:

`$impeccable shape risk alerts ArtDeco triage desk`

Shape should focus on:

- one primary risk-alert triage flow,
- compact header/status band,
- severity and unread control row,
- alert table as the primary surface,
- rule management as secondary configuration,
- live/stale/degraded/empty/error state grammar,
- preservation of current API and route contracts.

Do not run `$impeccable craft` until the shape brief is reviewed and explicitly approved.
