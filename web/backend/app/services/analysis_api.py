"""Service wrapper for analysis data API classes."""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


def _load_analysis_api_module():
    module_path = Path(__file__).resolve().parents[1] / "api" / "data" / "analysis_api.py"
    if not module_path.exists():
        return None
    spec = spec_from_file_location("app.api.data.analysis_api", module_path)
    if spec is None or spec.loader is None:
        return None
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_module = _load_analysis_api_module()


if _module:
    AnalysisDataService = getattr(_module, "AnalysisDataService", None)
    IndicatorType = getattr(_module, "IndicatorType", None)
    TimePeriod = getattr(_module, "TimePeriod", None)
    AnalysisType = getattr(_module, "AnalysisType", None)
    IndicatorData = getattr(_module, "IndicatorData", None)
    FundamentalData = getattr(_module, "FundamentalData", None)
    AnalysisResult = getattr(_module, "AnalysisResult", None)
else:

    class AnalysisDataService:  # type: ignore[no-redef]
        """Fallback AnalysisDataService when api/data module is unavailable."""

        def __init__(self, *args, **kwargs):
            pass

    IndicatorType = None
    TimePeriod = None
    AnalysisType = None
    IndicatorData = None
    FundamentalData = None
    AnalysisResult = None
