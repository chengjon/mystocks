from app.quotes_payload import build_quotes_response_payload


def test_build_quotes_response_payload_unwraps_nested_data_list():
    payload = {
        "data": {
            "data": [
                {
                    "symbol": "000001",
                    "name": "平安银行",
                    "price": 12.34,
                    "change_percent": 1.2,
                    "volume": 1000000,
                    "amount": 1200000000,
                }
            ],
            "total": 1,
            "timestamp": "2026-03-13T00:00:00",
        }
    }

    result = build_quotes_response_payload(payload, ["000001"])

    assert result["total"] == 1
    assert isinstance(result["quotes"], list)
    assert result["quotes"][0]["symbol"] == "000001"


def test_build_quotes_response_payload_falls_back_when_rows_are_empty():
    payload = {
        "data": {
            "data": [],
            "total": 0,
            "timestamp": "2026-03-13T00:00:00",
        }
    }

    result = build_quotes_response_payload(payload, ["000001", "600519"])

    assert result["total"] == 2
    assert len(result["quotes"]) == 2
    assert result["quotes"][0]["symbol"] == "000001"
    assert "price" in result["quotes"][0]
