# Gemini CLI: Python Quality Assurance Guidelines

This document outlines the Python code quality assurance workflow and tools that Gemini CLI must adhere to when working on Python projects. These guidelines are derived from the project's official quality assurance documentation (`docs/guides/PYTHON_QUALITY_ASSURANCE_WORKFLOW.md`, `docs/guides/PYTHON_QUALITY_TOOLS_QUICK_REFERENCE.md`, and `CLAUDE.md`).

## Core Principles

-   **Ruff First**: Prioritize Ruff for daily development for speed and efficiency.
-   **Black as Fallback**: Use Black to ensure consistent code formatting, especially in pre-commit.
-   **Pylint for Deep Analysis**: Utilize Pylint for in-depth code quality checks, typically run periodically.
-   **Security Mandatory**: Bandit and Safety are critical and must always be used.
-   **Unified Configuration**: All tools adhere to a 120-character line length.

## Four-Stage Quality Assurance Process for Gemini CLI

Gemini CLI must integrate and respect the following four-stage quality assurance process:

### Stage 1: Daily Development (Efficiency First)

**Objective**: Rapidly fix code issues without hindering development speed.

**Tool**: Ruff (all-in-one formatter + linter)

**Trigger**: After any code modification or when asked to fix formatting/linting issues.

**Action**:
-   To fix all auto-fixable issues: `ruff check --fix .`
-   To format code: `ruff format .`
-   To check without fixing: `ruff check .`

### Stage 2: Pre-commit Checks (Automated Enforcement)

**Objective**: Ensure committed code adheres to team standards.

**Tool**: Pre-commit Hooks (automatically triggered by `git commit`)

**Action**:
-   Before committing, ensure that pre-commit hooks are installed (`pre-commit install`).
-   When making a commit, allow pre-commit hooks to run. If a commit fails due to pre-commit, address the reported issues.
-   To manually run all checks: `pre-commit run --all-files`

**Expected Hook Chain (Gemini CLI should be aware of this order):**
1.  Ruff (Lint & Fix)
2.  Black (Formatter)
3.  Ruff (Check only)
4.  MyPy (Type Check)
5.  Bandit (Security Scan)
6.  Safety (Dependency Check)
7.  General file checks (trailing whitespace, YAML/JSON syntax)
8.  Secret detection
9.  Python syntax checks (blanket noqa/eval, etc.)

### Stage 3: Periodic Deep Quality Analysis

**Objective**: Identify deeper code quality issues that might be missed by faster checks.

**Tool**: Pylint (using a test-specific configuration)

**Trigger**: When specifically asked to perform a deep code analysis, or during phase completion verification for test code.

**Action**:
-   To check test code quality: `pylint --rcfile=.pylint.test.rc tests/`
-   To generate an HTML report for test code: `pylint --rcfile=.pylint.test.rc --output=pylint_test_report.html --output-format=html tests/`
-   To check source code: `pylint src/` (using `.pylintrc`)

### Stage 4: CI/CD Integration (Reference Only)

**Objective**: Understand the CI/CD strategy for quality gates.

**Gemini CLI Role**: Be aware that CI/CD pipelines will enforce these checks. Ruff/Black failures lead to quick pipeline failures. MyPy/Bandit/Safety are core checks. Pylint typically generates reports without blocking the build.

## Configuration Files to Reference

-   `pyproject.toml`: Ruff, Black, MyPy, Pylint (general) configurations.
-   `.pylint.test.rc`: Pylint configuration specifically for test code.
-   `.pre-commit-config.yaml`: Configuration for pre-commit hooks.
-   `config/.security.yml`: Security configuration for Bandit.

## When Making Code Changes

-   Always consider the appropriate stage of the workflow.
-   Prioritize Ruff for quick fixes and formatting during implementation.
-   Ensure `pre-commit` passes before finalizing any code changes in a commit.
-   Be mindful of the configured line length (120 characters).
-   When adding new tests, ensure they meet Pylint standards as defined in `.pylint.test.rc`.
