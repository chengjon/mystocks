# CI Dependency Safety Manifest Alignment

Date: 2026-06-13
Task: G2.333
Mode: source-free dependency manifest fix
Base worktree: `g2-333-ci-dependency-safety-manifest-alignment`
Base commit: `dfeb6b2963aa2ca991dceb3cc3058e26461a80a0`

## Status

G2.333 isolates dependency manifest alignment required by the CI `Dependency
Safety Check`. It updates only the requirement files scanned by that job:

- `requirements.txt`
- `config/requirements.txt`
- `web/backend/requirements.txt`

No MyStocks API source, frontend source, tests, scripts, runtime behavior,
OpenSpec implementation files, or OpenStock internals are changed.

## Dependency Changes

| Package | Previous specifier(s) | Safety affected spec | Updated specifier(s) |
| --- | --- | --- | --- |
| `APScheduler` | Present only in `web/backend/requirements.txt` | N/A; needed for backend cache eviction imports in api-file-tests | `APScheduler>=3.10.4` added to root `requirements.txt` |
| `python-dotenv` | `>=1.0.0` / `==1.0.1` | `<1.2.2` | `>=1.2.2` / `==1.2.2` |
| `requests` | `>=2.32.4` / `==2.32.4` | `<2.33.0` | `>=2.33.0` / `==2.33.0` |
| `python-multipart` | `>=0.0.22` / `==0.0.22` | `<0.0.27` | `>=0.0.27` / `==0.0.27` |
| `pytest` | `>=7.4.0` / `==8.3.0` | `<9.0.3` | `>=9.0.3` / `==9.0.3` |
| `pytest-asyncio` | `==0.24.0` | N/A; pip resolver compatibility with pytest 9 | `==1.4.0` |

PyPI availability was checked for the required safety lower bounds:

- `pytest`: latest/available includes `9.0.3`
- `python-multipart`: available includes `0.0.27`
- `requests`: available includes `2.33.0`
- `python-dotenv`: latest/available includes `1.2.2`
- `pytest-asyncio`: latest/available includes `1.4.0`; pip dry-run confirmed compatibility with `pytest==9.0.3`

## Function-Tree Catalog Note

The manifest fix maps to `domain-08-node-02` because it changes system
dependency configuration used by CI/runtime setup. `config/**` was already
covered by that node. G2.333 adds `requirements.txt` and
`web/backend/requirements.txt` literal coverage so mainline gate attribution is
explicit.

## Verification

| Check | Result |
| --- | --- |
| `python -c "assert CI-scanned dependency lower bounds are present"` | Required lower bounds and `pytest-asyncio==1.4.0` present in scanned manifests |
| `safety check -r requirements.txt -r config/requirements.txt -r web/backend/requirements.txt` | 0 vulnerabilities reported; ignored unpinned warning ranges unchanged |
| `python governance/mainline/scripts/mainline_scope_gate.py --task-card governance/mainline/task-cards/g2-333.yaml --schema governance/mainline/schemas/ai-task-card.schema.json --base-sha HEAD~1 --head-sha HEAD --report /tmp/g2-333-mainline-gate.json` | To be run after commit |
| `gitnexus_detect_changes(scope=compare, base_ref=origin/main)` | To be run after commit |
| `git diff HEAD~1..HEAD --check` | To be run after commit |

## Rollback

Revert the G2.333 commit to restore previous dependency specifiers and catalog
metadata.
