# Q2 Phase E Function Tree And Evidence Hardening Audit

Date: 2026-04-25
Scope: `plan-q2-optimization-closure-program` Phase E
Mode: single-CLI sequential audit

## Documents And Code Surfaces Examined
- `docs/FUNCTION_TREE.md`
- `governance/function-tree/catalog.yaml`
- `governance/function-tree/schema.json`
- `architecture/STANDARDS.md`
- `openspec/specs/function-tree-governance/spec.md`
- `openspec/specs/code-quality/spec.md`
- `docs/reports/quality/Q2_PHASE_A_REALTIME_TRUTH_AUDIT_2026-04-25.md`
- `docs/reports/quality/Q2_PHASE_B_BACKEND_COMPOSITION_CLOSURE_2026-04-25.md`
- `docs/reports/quality/Q2_PHASE_C_DATA_QUALITY_UNIFICATION_2026-04-25.md`
- `docs/reports/quality/Q2_PHASE_D_TRADING_SAFETY_CONTRACT_2026-04-25.md`

## Executive Summary
The current function-tree governance stack is strong on catalog structure and scope mapping, but weak on evidence-backed completion semantics.

Current repo truth:
- `governance/function-tree/catalog.yaml` and `schema.json` govern stable IDs, node coverage, and scope validation
- `docs/FUNCTION_TREE.md` presents domain status and completion percentages
- the existing base spec does not define how completion percentages or "✅ 完成 / 生产可用" claims must be justified

This creates a governance gap: the machine-readable catalog can say where a change belongs, but it cannot say whether the function-tree status claim is defensible.

## Key Findings

### 1. Existing function-tree governance focuses on mapping, not completion proof
The current base spec requires:
- stable domain and node identifiers
- task-card mapping
- scope gate consistency
- mirrored domain sync duties

It does not require:
- evidence classes behind completion percentages
- explicit distinction between implementation-complete and production-ready
- safety-sensitive downgrade logic

### 2. `docs/FUNCTION_TREE.md` already uses strong status language
The legend currently states:
- `✅ 完成`: 功能已实现，测试通过，生产可用

That is much stronger than "implemented in code" and much stronger than "main flow exists".

Given the Q2 A-D audit findings, this wording is too strong to be treated as a generic default without evidence gates.

### 3. Domain 05 is the clearest conflict case
`docs/FUNCTION_TREE.md` currently marks:
- `05-投资组合与交易`
- status: `🚧 开发中`
- completion: `70%`

This is directionally better than marking it complete, but individual sub-capabilities inside the domain still include several `✅` rows. After Phase D, any function-tree interpretation touching real execution or execution tracking must distinguish:
- implemented UI or modeled logic
- experimental execution path
- production-eligible execution path

Without that distinction, the function tree can accidentally overstate readiness.

### 4. A-D audit outputs are the missing evidence inputs
The Q2 closure program has now produced evidence from four prior phases:
- Phase A: realtime truth audit
- Phase B: backend composition truth audit
- Phase C: data quality ownership audit
- Phase D: trading safety contract audit

These reports are exactly the kind of artifacts needed to support or block function-tree status claims.

### 5. Percentages currently lack a declared calculation model
`docs/FUNCTION_TREE.md` uses domain percentages such as 95%, 85%, 70%, 50%, but no formal rule defines whether these are based on:
- route coverage
- API implementation
- test coverage
- E2E pass rate
- runtime readiness
- production safety or governance proof

The percentages are therefore informative but not auditable.

## Criteria-Backed Completion Model Recommendation

Each function-tree domain or node should classify evidence into four layers:

| Evidence layer | Meaning |
|---|---|
| implementation evidence | code path exists and is wired |
| verification evidence | tests, smoke, or E2E verify expected behavior |
| runtime evidence | route/service/runtime path is actually canonical and reachable |
| safety/governance evidence | required contracts, risk gates, and truth-source audits are satisfied |

### Recommended status interpretation
- `📝 计划中`
  - intent exists, implementation evidence missing
- `🚧 开发中`
  - partial implementation evidence exists, but verification or runtime evidence incomplete
- `🧪 实验性`
  - implementation exists, but runtime/safety/governance evidence is intentionally incomplete or unstable
- `✅ 完成`
  - implementation, verification, and runtime evidence are satisfied
  - safety/governance evidence must also be satisfied if the node is safety-sensitive
- `⚠️ 需修复`
  - previously valid evidence is now contradicted by defects, regressions, or broken truth sources
- `🔒 已废弃`
  - no longer canonical and documented as retired

## Safety-Sensitive Rule
For function-tree purposes, a node is safety-sensitive if it involves:
- funds movement
- position change
- pre-execution risk decisions
- production-eligible trading path claims

For such nodes:
- implementation evidence alone is never enough for `✅ 完成`
- production-usable wording must be blocked if the trading safety contract is unresolved

## Required Closure Evidence For Function-Tree Updates

Any domain or node status upgrade should record at least:
- canonical path or truth source
- verification artifacts used
- runtime route or service evidence
- unresolved gaps and why they do not block the claimed status

For safety-sensitive nodes it must also record:
- audit or safety contract status
- whether the path is simulated, experimental, or production-eligible
- explicit reasons if production-eligibility is denied

## Recommended Interpretation For Current Q2 Domains

### Domain 05: 投资组合与交易
- Keep domain-level status conservative.
- Real execution and execution-tracking related capabilities should be interpreted as experimental or in-progress unless and until Phase D conditions are satisfied.

### Domain 06: 监控与告警
- Quality-related `✅` claims should be interpreted through the Phase C ownership split.
- Monitoring presence alone should not imply repair/backfill closure.

### Domain 01 realtime-related nodes
- Realtime push claims should align with the Phase A canonical transport result.
- Socket.IO-specific capability claims must not be treated as canonical runtime proof yet.

## Recommended Next Steps
1. Update OpenSpec governance to explicitly bind function-tree status claims to evidence classes.
2. Treat current function-tree percentages as historical or operational snapshots unless backed by declared evidence.
3. Use the A-D audit reports as the first closure-wave evidence set for Q2-sensitive domains.
4. Avoid upgrading safety-sensitive nodes to `✅ 完成` when only modeled logic or UI coverage exists.
