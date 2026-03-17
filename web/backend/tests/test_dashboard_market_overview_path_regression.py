import ast
from pathlib import Path


def _load_market_overview_calls() -> set[str]:
    dashboard_path = Path(__file__).resolve().parents[1] / "app" / "api" / "dashboard.py"
    source = dashboard_path.read_text(encoding="utf-8")
    tree = ast.parse(source)

    for node in tree.body:
        if isinstance(node, ast.AsyncFunctionDef) and node.name == "get_market_overview":
            attr_calls = {
                child.attr
                for child in ast.walk(node)
                if isinstance(child, ast.Attribute) and isinstance(child.ctx, ast.Load)
            }
            name_calls = {
                child.id for child in ast.walk(node) if isinstance(child, ast.Name) and isinstance(child.ctx, ast.Load)
            }
            return attr_calls | name_calls

    raise AssertionError("get_market_overview route not found in dashboard.py")


def test_market_overview_route_avoids_full_dashboard_summary_path() -> None:
    calls = _load_market_overview_calls()

    assert "get_dashboard_summary" not in calls
    assert "get_market_overview_data" in calls
    assert "build_market_overview" in calls
