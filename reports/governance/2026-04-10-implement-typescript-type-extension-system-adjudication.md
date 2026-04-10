# Adjudication: implement-typescript-type-extension-system

> **治理裁定说明**:
> 本文件用于记录 2026-04-10 对 `implement-typescript-type-extension-system` 的当前治理判断。
> 共享规则仍以 `architecture/STANDARDS.md` 为准；本文件只回答该 active change 是否应继续保留，以及应如何理解其边界。

## Decision

Keep `implement-typescript-type-extension-system` active, but treat it as a narrowed auxiliary line that complements automatic type generation rather than replacing it.

## Why It Should Stay

- The change is structurally valid: `openspec validate implement-typescript-type-extension-system --strict` passes.
- Current repo evidence shows partial implementation already exists:
  - `web/frontend/src/api/types/extensions/`
  - `web/frontend/src/api/types/tools/validators/TypeValidator.ts`
  - `web/frontend/package.json` scripts `type:validate` and `type:check:conflicts`
- Its capability boundary is still meaningful: frontend-specific extension types are not the same problem as backend-schema-driven automatic generation covered by `openspec/specs/02-type-safety-generation/spec.md`.

## Why It Must Not Be Read As Fully Executed

Current repo truth still diverges from the original proposal/tasks/design in several places:

- `web/frontend/src/api/types/index.ts` does not re-export `./extensions`, so the promised unified import surface is incomplete.
- The implemented extension structure does not match the planned directory shape.
- Validator assumptions are partially stale; for example it expects files that do not exist in the current tree.
- Pre-commit integration for type-extension validation is not evidenced.
- Proposal/tasks/design/spec files contain tool-residue fragments, so their text should not be treated as exact execution truth.

## Relationship To Existing Type Trunks

- `openspec/specs/02-type-safety-generation/spec.md` remains the trunk for backend-to-frontend automatic type generation.
- This change should only govern the manual extension layer for frontend-specific ViewModel or utility types that generated schemas cannot provide cleanly.
- It should not create a parallel type-truth system that competes with generated types.

## Execution Rule For Future Sessions

- Do not retire this change as stale.
- Do not claim it complete from the presence of partial code.
- Do not continue its original checklist mechanically.
- If execution resumes, first rewrite the task surface against current repo truth:
  - align actual extension file layout
  - wire exports through `web/frontend/src/api/types/index.ts`
  - reconcile validator expectations with the real directory structure
  - decide whether hook / CI integration is still required in the current frontend pipeline
