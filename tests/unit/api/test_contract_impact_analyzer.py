from __future__ import annotations

import os
import sys


sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../web/backend"))

from app.api.contract.services.impact_analyzer import ContractImpactAnalyzer


def test_contract_impact_analyzer_reports_removed_endpoint_and_client_impact() -> None:
    from_spec = {
        "openapi": "3.1.0",
        "paths": {
            "/api/v1/market/quotes": {
                "get": {
                    "operationId": "getMarketQuotes",
                    "tags": ["market"],
                    "responses": {"200": {"description": "ok"}},
                }
            },
            "/api/v1/system/health": {
                "get": {
                    "operationId": "getSystemHealth",
                    "tags": ["system"],
                    "responses": {"200": {"description": "ok"}},
                }
            },
        },
        "components": {"schemas": {}},
    }
    to_spec = {
        "openapi": "3.1.0",
        "paths": {
            "/api/v1/system/health": {
                "get": {
                    "operationId": "getSystemHealth",
                    "tags": ["system"],
                    "responses": {"200": {"description": "ok"}},
                }
            }
        },
        "components": {"schemas": {}},
    }

    analysis = ContractImpactAnalyzer().analyze_specs(from_spec, to_spec, "1.0.0", "2.0.0")

    assert analysis.risk_level == "critical"
    assert analysis.summary.breaking_impacts == 1
    assert analysis.affected_endpoints == ["/api/v1/market/quotes"]
    assert analysis.affected_clients == ["market"]
    assert analysis.impacts[0].category == "endpoint"
    assert analysis.impacts[0].change_type == "removed"
    assert analysis.impacts[0].is_breaking is True


def test_contract_impact_analyzer_reports_schema_property_removal() -> None:
    from_spec = {
        "openapi": "3.1.0",
        "paths": {},
        "components": {
            "schemas": {
                "QuoteResponse": {
                    "type": "object",
                    "required": ["symbol", "price"],
                    "properties": {
                        "symbol": {"type": "string"},
                        "price": {"type": "number"},
                    },
                }
            }
        },
    }
    to_spec = {
        "openapi": "3.1.0",
        "paths": {},
        "components": {
            "schemas": {
                "QuoteResponse": {
                    "type": "object",
                    "required": ["symbol"],
                    "properties": {
                        "symbol": {"type": "string"},
                    },
                }
            }
        },
    }

    analysis = ContractImpactAnalyzer().analyze_specs(from_spec, to_spec, "1.0.0", "1.1.0")

    assert analysis.risk_level == "high"
    assert analysis.summary.breaking_impacts == 1
    assert analysis.affected_schemas == ["QuoteResponse"]
    assert analysis.impacts[0].category == "schema"
    assert analysis.impacts[0].name == "QuoteResponse.price"
    assert "removed" in analysis.recommendations[0]
