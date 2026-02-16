# Hardcoding Governance Weekly Report

- Week ending: `2026-02-15`
- Scope: `runtime` (`src/`, `web/backend/app/`, `web/frontend/src/`, `config/pm2*`, `config/tdx_settings.conf`)
- Plan reference: `docs/plans/2026-02-15-mystocks-hardcoding-governance-plan.md`

## Summary

- Implemented scanner + rules + exception lifecycle validator.
- Added pre-commit and CI hardcoding gates.
- Completed first remediation wave for P0 credentials/default secrets.
- Completed endpoint centralization groundwork for frontend and TDX server pool externalization.

## Metrics

- Initial session baseline (pre-remediation): `P0=43`, `P1=347`, `P2=86`, `total=476`
- Current baseline (`reports/security/hardcoding/baseline-2026-02-15.json`):
  - `P0=0`
  - `P1=339`
  - `P2=85`
  - `total=424`

## Delivered This Week

- New files:
  - `scripts/security/hardcoding_scan.py`
  - `scripts/security/validate_hardcoding_exceptions.py`
  - `config/security/hardcoding-rules.yml`
  - `config/security/hardcoding_exceptions.yml`
  - `config/tdx_servers.yaml`
  - `reports/security/hardcoding/baseline-2026-02-15.json`
  - `reports/security/hardcoding/baseline-2026-02-15.md`
  - `web/frontend/src/config/runtime-endpoints.ts`
- Updated governance integrations:
  - `.pre-commit-config.yaml`
  - `.github/workflows/code-quality.yml`
- Key runtime P0 remediations: backend encryption/system DB checks, PM2 envs, GPU config/entrypoint, TDengine defaults.

## Exceptions

- Active exceptions: `0`
- Expired exceptions: `0`

## Remaining Focus (Next Week)

1. Continue P1 reduction in broader backend runtime modules (outside first target batch).
2. Reduce P2 by replacing residual localhost/loopback literals with config helpers or approved allowlist.
3. Start weekly automated delta reporting from CI artifact.
