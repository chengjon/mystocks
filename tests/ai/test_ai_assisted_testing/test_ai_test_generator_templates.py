from __future__ import annotations

from tests.ai.test_ai_assisted_testing.ai_test_generator_methods import AITestGenerator
from tests.ai.test_ai_assisted_testing.helpers import AnalysisResult


def _build_analysis(method_name: str = "calculate_value") -> AnalysisResult:
    return AnalysisResult(
        method_name=method_name,
        complexity=1,
        length=1,
        cyclomatic_complexity=1,
        cognitive_complexity=1,
        coupling_score=0.1,
        cohesion_score=0.9,
        test_coverage=[],
        dependencies=[],
        risk_level="low",
        security_issues=[],
        performance_issues=[],
        maintainability_score=0.9,
    )


def test_ai_test_generator_can_be_imported_and_instantiated() -> None:
    generator = AITestGenerator()

    assert generator.context_analyzer is not None
    assert generator.pattern_library


def test_part2_generated_templates_use_smoke_assertions_instead_of_placeholders() -> None:
    generator = AITestGenerator()
    analysis = _build_analysis("calculate_value")

    generated_snippets = [
        generator._generate_basic_test_case(analysis),
        generator._generate_parameter_validation_test(analysis),
        generator._generate_return_validation_test(analysis),
        generator._generate_boundary_test_case(analysis),
        generator._generate_recursive_test("recursive_sum"),
        generator._generate_async_test("async_fetch"),
    ]

    placeholder_token = "assert" + " True"
    assert all(placeholder_token not in snippet for snippet in generated_snippets)
    assert all("assert callable(target)" in snippet for snippet in generated_snippets)
