from __future__ import annotations

import importlib
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
BACKEND_ROOT = ROOT / "web" / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


def _load_module():
    sys.modules.pop("app.api.v1.analysis.sentiment", None)
    return importlib.import_module("app.api.v1.analysis.sentiment")


async def test_v1_sentiment_analyze_returns_runtime_scores():
    module = _load_module()
    module._SENTIMENT_HISTORY.clear()
    request = module.SentimentRequest(
        symbol="0700.HK",
        text="腾讯云收入增长明显，广告恢复强劲，市场看好长期回报",
        source="broker-report",
    )

    payload = await module.analyze_sentiment(request)

    assert payload.success is True
    assert payload.code == 200
    assert payload.data["symbol"] == "0700.HK"
    assert payload.data["sentiment"] == "positive"
    assert payload.data["positive_score"] > payload.data["negative_score"]
    assert payload.data["key_phrases"]


async def test_v1_stock_sentiment_returns_runtime_aggregation():
    module = _load_module()
    module._SENTIMENT_HISTORY.clear()
    await module.analyze_sentiment(module.SentimentRequest(symbol="600519", text="业绩增长，需求恢复，市场看好", source="news"))
    await module.analyze_sentiment(module.SentimentRequest(symbol="600519", text="利润改善，回报提升", source="news"))

    payload = await module.get_stock_sentiment("600519")

    assert payload.success is True
    assert payload.code == 200
    assert payload.data["symbol"] == "600519"
    assert payload.data["mentions"] >= 2
    assert payload.data["trend"] in {"positive", "neutral", "negative"}
    assert payload.data["timeline"]


async def test_v1_market_sentiment_returns_runtime_overview():
    module = _load_module()
    module._SENTIMENT_HISTORY.clear()
    await module.analyze_sentiment(module.SentimentRequest(symbol="600519", text="增长恢复，市场看好", source="news"))
    await module.analyze_sentiment(module.SentimentRequest(symbol="000001", text="业务承压，风险上升", source="news"))

    payload = await module.get_market_sentiment()

    assert payload.success is True
    assert payload.code == 200
    assert payload.data["coverage"] >= 2
    assert set(payload.data["hot_symbols"]) >= {"600519", "000001"}
