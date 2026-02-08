# Tech Debt Governance Execution Board (2026Q1)

## Usage
- Cadence: weekly plan (Mon) and rollup (Fri)
- Status: todo | doing | blocked | done
- Priority: P0 (2 weeks) | P1 (30 days) | P2 (90 days)
- Evidence: doc path, PR, CI, or dashboard link

| ID | Task | Priority | Owner | DDL | Dependencies | Status | Acceptance Criteria | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| T01 | Define Architecture Source of Truth | P0 | main | 2026-02-20 | - | doing | SoT doc created and reviewed | `technical_debt/governance/ARCHITECTURE_SOURCE_OF_TRUTH.md` |
| T02 | Seed Spec Conflict Matrix (Round 1) | P0 | main | 2026-02-22 | T01 | doing | SC-001..SC-010 tracked with owner/status | `technical_debt/governance/SPEC_CONFLICT_MATRIX.md` |
| T03 | Establish Debt Register Cadence | P0 | main | 2026-02-23 | T01 | doing | TD-001..TD-015 have owner/DDL fields | `technical_debt/governance/DEBT_REGISTER.md` |
| T04 | Consolidate Runtime Config Entry Points | P0 | main | 2026-02-26 | T01,T02 | doing | Single config entry point documented | `technical_debt/governance/CONFIG_ENTRYPOINT_INVENTORY.md` |
| T05 | API Contract Baseline and Drift Checks | P1 | cli-2 | 2026-03-05 | T02 | todo | Contract checks added to CI | TBD |
| T06 | Data Routing Rules + Regression Tests | P1 | main+cli-6 | 2026-03-08 | T01,T04 | todo | Routing rules documented + tests | TBD |
| T07 | Minimum Observability SLO Baseline | P1 | main | 2026-03-10 | T04 | todo | 2 core SLOs defined and tracked | TBD |
| T08 | Tooling Entry Point De-duplication | P1 | main | 2026-03-12 | T03 | todo | Unified tooling entry points | TBD |
| T09 | Debt Gate (PR) Trial | P2 | main | 2026-04-01 | T05,T06,T07 | todo | PR gate enabled for debt checks | TBD |
| T10 | Monthly Governance Report Automation | P2 | main | 2026-04-15 | T03,T09 | todo | Automated monthly report | TBD |

## This Week (Suggested)
1. T01 (SoT draft)
2. T02 (Conflict matrix seed)
3. T03 (Debt register seed)
4. T04 (Config consolidation plan)
