"""Service wrapper for Data API classes."""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


def _load_data_api_module():
    module_path = Path(__file__).resolve().parents[1] / "api" / "data" / "data_api_new.py"
    if not module_path.exists():
        return None
    spec = spec_from_file_location("app.api.data.data_api_new", module_path)
    if spec is None or spec.loader is None:
        return None
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_module = _load_data_api_module()


if _module and hasattr(_module, "DataApiService"):
    DataApiService = _module.DataApiService
else:

    class DataApiService:  # type: ignore[no-redef]
        """Fallback DataApiService when api/data module is unavailable."""

        def __init__(self, *args, **kwargs):
            pass
