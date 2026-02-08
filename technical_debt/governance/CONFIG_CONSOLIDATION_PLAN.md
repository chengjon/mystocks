# Config Consolidation Plan (T04)

## Goal
Establish a single, authoritative backend config entry point and eliminate duplicated config loaders.

## Primary Entry Point
- Backend runtime config: `web/backend/app/core/config.py`
- Registry SoT format: YAML (`config/data_sources_registry.yaml`)

## Scope
- Centralize `.env` loading and typed settings in the primary entry point.
- Route YAML/JSON registry reads through a shared loader.
- Deprecate direct `load_dotenv()` calls in non-entry modules.

## Phased Timeline

### Phase 1: Unification (Day 0-14)
- Document the primary entry point and SoT registry format.
- Add deprecation warnings in secondary loaders.
- Update services to call the shared loader instead of direct YAML/JSON reads.

### Phase 2: Deprecation (Day 15-60)
- Remove direct JSON registry reads from services.
- Remove ad-hoc `.env` loading outside the primary entry point.
- If JSON registry is still needed, generate it from YAML as a build artifact.

## Compatibility
- Provide a temporary compatibility shim for legacy JSON paths.
- Keep shims for one release cycle, then remove after migration.

## Acceptance Criteria
- Single backend entry point documented and referenced in SoT.
- All registry reads go through shared loader.
- No direct `.env` loads outside entry point.
- CI guard prevents new direct registry reads.

## Evidence
- `technical_debt/governance/CONFIG_ENTRYPOINT_INVENTORY.md`
- `technical_debt/governance/ARCHITECTURE_SOURCE_OF_TRUTH.md`
- `technical_debt/governance/CONFIG_CONSOLIDATION_PLAN.md`
