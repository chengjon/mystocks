# Redis / Mongo Runtime Convergence Closure

> Date: 2026-03-12
> Status: Closure summary
> Scope: Redis / Mongo runtime configuration, readiness, health exposure, deployment assets, and verification scripts

## 1. Objective

This workstream converged Redis and MongoDB runtime behavior toward a single governance baseline:

- Redis uses role-aware DB resolution instead of a single implicit `REDIS_DB` assumption
- MongoDB remains optional by default and visible in runtime health checks without becoming a readiness blocker
- deployment assets, runtime scripts, and code paths stop drifting on ports, client commands, and config file expectations

## 2. Completed Convergence

### 2.1 Runtime Helpers

Implemented or extended:

- `src/utils/redis_runtime_config.py`
- `src/utils/mongo_runtime_config.py`

Result:

- Redis now supports role-aware resolution:
  - `app_cache`
  - `monitoring_events`
  - `tooling_maintenance`
  - `celery_broker`
  - `celery_result`
- Mongo now supports:
  - standard env names first
  - compatibility fallback from legacy aliases

### 2.2 Core Runtime Paths

Converged code paths:

- `src/storage/database/connection_manager.py`
- `web/backend/app/core/redis_client.py`
- `src/core/data_source/registry.py`
- `src/core/datasource/registry.py`
- `web/backend/app/core/cache/multi_level.py`
- `src/core/cache/multi_level.py`
- `src/monitoring/async_monitoring.py`
- `src/storage/database/db_utils.py`
- `src/storage/database/database_manager/database_table_manager_methods/part1.py`
- `web/backend/app/services/cache_service.py`
- `src/application/bootstrap.py` (previously verified in governance tests)
- `src/gpu/api_system/utils/redis_utils.py` and `src/gpu/api_system/utils/cache_optimization.py` were confirmed already aligned to `tooling_maintenance`

Result:

- hardcoded `redis://localhost:6379` defaults were removed from active cache paths
- Redis connections now resolve via explicit logical roles where this workstream touched the code
- YAML datasource registration now uses `endpoint_name` as canonical key, removing alias duplication in runtime registry

### 2.3 Mongo Runtime Exposure

Converged code paths:

- `web/backend/app/core/config.py`
- `web/backend/app/core/readiness.py`
- `web/backend/app/api/health.py`

Result:

- MongoDB standard config fields now exist in backend settings
- readiness exposes Mongo status but keeps it `required: false`
- `/health` now also shows Mongo status with the same optional boundary semantics

### 2.4 Runtime Health Scripts

Implemented:

- `scripts/dev/check_mongodb_runtime_health.sh`
- `scripts/dev/check_redis_runtime_health.sh`

Result:

- Mongo health uses `mongosh`
- Redis runtime health explicitly checks:
  - `REDIS_APP_CACHE_DB`
  - `REDIS_MONITORING_DB`
- Both scripts support docker-based fallback execution in the current WSL2 environment

### 2.5 Deployment Assets And Docs

Converged assets:

- `config/docker/mongodb.yml`
- `config/docker/monitoring-stack.yml`
- `config/docker/docker-compose.prod.yml`
- `config/docker/README.md`
- `config/docker/QUICK_REFERENCE.md`
- `config/docker-infra/mongodb.yml`
- `config/docker-infra/monitoring-stack.yml`
- `config/docker-infra/README.md`
- `config/docker-infra/QUICK_REFERENCE.md`
- `config/mongodb/mongod.conf`
- `config/redis/redis.conf`

Result:

- Mongo baseline now documents and configures port `27017`
- Mongo health checks use `mongosh`, not `mongo`
- Redis docs now expose role-aware DB variables
- missing runtime config files for Mongo and Redis now exist in the repo

## 3. Governance Documents Added Or Confirmed

Authoritative references now available:

- `docs/reports/REDIS_MONGO_RUNTIME_CONFIG_REQUIREMENTS_20260312.md`
- `docs/reports/MONGODB_SCOPE_AND_EVIDENCE_GATE.md`
- `reports/DATA_SOURCE_INSPECTION_REPORT_REMEDIATED_2026-03-12.md`

These documents establish:

- Redis role matrix
- Mongo optional-boundary policy
- standard variable precedence
- evidence gate for any future Mongo-backed feature

## 4. Verification Evidence

### 4.1 Targeted Test Suites

Executed and passing:

- `tests/unit/core/test_runtime_config_governance.py` -> `8 passed`
- `tests/unit/core/test_web_backend_runtime_settings.py` -> `3 passed`
- `tests/unit/adapters/test_runtime_data_source_regressions.py` -> `5 passed`
- `tests/unit/core/test_mongodb_runtime_entry.py` -> `3 passed`
- `tests/unit/core/test_health_mongodb_optional.py` -> `2 passed`
- `tests/unit/core/test_mongodb_runtime_assets.py` -> `3 passed`
- `tests/unit/core/test_redis_runtime_assets.py` -> `3 passed`
- `tests/unit/core/test_redis_runtime_scripts.py` -> `2 passed`
- `tests/unit/core/test_web_backend_multilevel_cache_runtime.py` -> `3 passed`
- `tests/unit/core/test_src_core_multilevel_cache_runtime.py` -> `2 passed`
- `tests/unit/core/test_datasource_registry_redis_runtime.py` -> `2 passed`
- `tests/unit/core/test_gpu_cache_redis_runtime.py` -> `2 passed`

Total targeted regression count verified in this workstream:

- `38 passed`

### 4.2 Runtime Script Verification

Verified in current environment:

- `scripts/dev/check_mongodb_runtime_health.sh` -> returned `{ ok: 1 }`
- `scripts/dev/check_redis_runtime_health.sh` -> returned `PONG` for both required Redis roles
- `bash -n scripts/dev/check_mongodb_runtime_health.sh` -> pass
- `bash -n scripts/dev/check_redis_runtime_health.sh` -> pass

### 4.3 Infrastructure Baseline

Confirmed during this workstream:

- Redis is reachable at `localhost:6379`
- MongoDB is reachable at `localhost:27017`
- PostgreSQL and TDengine remained available

## 5. Residual Non-Blocking Debt

The following items remain outside this closure scope:

### 5.1 Data Source Business Availability

- Byapi still returns `403`
- Tushare still lacks `TUSHARE_TOKEN`
- WebData still lacks a confirmed valid business probe

### 5.2 Broader Legacy Script Surface

Some older utility or analysis scripts may still reference legacy Redis assumptions or historical architecture language.

They are lower priority if they are not in active runtime or deployment paths.

### 5.3 Mongo Feature Enablement

MongoDB is still not approved as an active business storage dependency.

That is intentional.

The correct status remains:

- available infrastructure
- optional runtime visibility
- gated feature adoption

## 6. Acceptance Conclusion

For the stated scope, this workstream can be considered **functionally converged**.

Meaning:

- runtime configuration behavior is now materially more consistent
- readiness and health semantics for Mongo are explicit and non-blocking
- Redis role-aware DB behavior is present in the key runtime and tooling paths touched in this session
- deployment assets and verification scripts are aligned with current runtime reality

## 7. Recommended Next Step

Do **not** continue broad, unbounded Redis/Mongo cleanup by default.

Prefer one of these bounded next steps only if needed:

1. a separate pass on remaining low-value legacy scripts
2. a separate feature proposal if Mongo is ever needed for a real document-oriented output
3. a commit / PR preparation pass for the files already changed in this workstream
