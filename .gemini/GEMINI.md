# MyStocks Workspace Context

This file follows the Gemini CLI context guideline: keep only stable, project-level instructions here.

## Project
- Name: `MyStocks`
- Type: quant trading data platform (Python backend + Vue frontend)
- Root: `/opt/claude/mystocks_spec`

## Non-Negotiable Rules
- Read `architecture/STANDARDS.md` before any code change.
- Proposal-first rule applies to UI/UX, menu structure, and architecture changes.
- Do not introduce instructions that conflict with `architecture/STANDARDS.md`.

## Coding Workflow
- Prefer minimal, verifiable changes.
- Keep imports explicit and use project conventions.
- Run focused verification after edits (`pytest`, frontend tests, or targeted commands).
- Separate new regressions from existing technical debt when reporting quality status.

## Tooling Constraints
- Use only tools that Gemini CLI actually exposes in the current session.
- Do not assume external agent/tool names from other CLIs.
- For file search, prioritize `rg`.

## Context Hygiene
- Keep this file stable and concise.
- Do not append temporary task logs here; use task/report files for run-specific notes.
