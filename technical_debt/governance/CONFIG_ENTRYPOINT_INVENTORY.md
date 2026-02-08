# Config Entry Point Inventory

## Purpose
Identify current runtime configuration entry points and their loaders to support consolidation.

## Inventory (Initial)

### Environment Variables (.env / OS env)
- Loaders (python-dotenv):
  - `src/storage/database/db_utils.py`
  - `src/storage/database/connection_context.py`
  - `src/storage/database/connection_manager.py`
  - `src/storage/database/database_manager.py`
  - `src/storage/database/save_realtime_market_data.py`
  - `src/storage/database/save_realtime_market_data_simple.py`
  - `web/backend/load_env.py`
  - `web/backend/setup_database.py`
  - `web/backend/app/api/data_source_registry.py`
  - `web/backend/app/services/monitoring_service.py`

### Pydantic Settings (BaseSettings)
- `web/backend/app/core/config.py`
- `web/backend/debug_config.py`
- `web/backend/minimal_test.py`

### YAML Config Files
- `config/table_config.yaml` (loader: `src/core/config_driven_table_manager.py`)
- `config/indicators_registry.yaml` (loader: `src/indicators/indicator_factory.py`)
- `config/data_sources_registry.yaml` (loader: `src/core/data_source/base.py`, `src/core/data_source/config_manager.py`)
- `config/data_sources_registry.yaml` (loader: `web/backend/app/api/data_source_config.py`)
- YAML registry configs loaded in:
  - `src/core/config_loader.py`
  - `src/core/data_source/registry.py`
  - `web/backend/app/services/indicators/indicator_registry.py`
  - `web/backend/app/services/data_source_factory.py`
  - `web/backend/app/services/signals/strategies/registry.py`

### JSON Config Files
- `config/data_sources.json` (loader: `web/backend/app/core/data_source_manager.py`)
- `config/data_sources.json` (loader: `web/backend/app/services/data_source_factory.py`)

### Other Config Files
- `config/tdx_settings.conf` (loader: `src/adapters/tdx/config.py`, `src/interfaces/adapters/tdx/config.py`)

## Observations
- Multiple loaders read overlapping data source registry files (YAML + JSON).
- Environment variables are loaded in multiple modules without a single entry point.
- Backend uses both `BaseSettings` and direct YAML/JSON loaders.

## Next Steps
1. Select primary backend config entry point (candidate: `web/backend/app/core/config.py`).
2. Define a single authoritative data source registry format (YAML or JSON).
3. Deprecate secondary loaders and document migration path.
