from src.storage.database._test_database_menu_cli import run_database_test_menu


def test_run_database_test_menu_executes_tool_run_all_tests() -> None:
    events: list[str] = []

    class _FakeTool:
        def __init__(self) -> None:
            events.append("init")

        def run_all_tests(self) -> None:
            events.append("run_all_tests")

    run_database_test_menu(_FakeTool)

    assert events == ["init", "run_all_tests"]
