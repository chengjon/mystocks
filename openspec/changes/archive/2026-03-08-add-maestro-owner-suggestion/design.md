# Maestro Owner Suggestion Design

## Context

Owner-aware dispatch already exists, but ownership choice still begins as a human decision. The next
step is to help the main CLI with a rule-based suggestion layer that remains advisory.

## Goals / Non-Goals

- Goals:
  - reduce repetitive ownership lookup work
  - stay deterministic and explainable
  - keep main CLI in control
- Non-Goals:
  - fully understand arbitrary natural-language tasks
  - auto-assign based on suggestion alone

## Decisions

1. use `.FILE_OWNERSHIP` as the primary source of truth
2. derive path hints from `TASK.md` and explicit CLI paths
3. default unknown paths to `main`
4. expose reasons in the output

## Risks / Trade-offs

- suggestions are only as good as path hints
- sparse `TASK.md` files may produce conservative results

## Migration Plan

1. add parser + suggester
2. expose CLI
3. optionally feed suggestion into future UI/API surfaces
