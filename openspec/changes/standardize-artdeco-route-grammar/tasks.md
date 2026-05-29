## 1. Proposal Validation

- [x] 1.1 Review current ArtDeco page-pilot extraction analysis.
- [x] 1.2 Review existing `artdeco-design-governance` spec.
- [x] 1.3 Create the OpenSpec proposal, design note, task list, and spec delta.
- [x] 1.4 Run `openspec validate standardize-artdeco-route-grammar --strict`.
- [ ] 1.5 Present the proposal for approval before implementation.

## 2. Documentation Implementation After Approval

- [ ] 2.1 Add the route grammar to the appropriate ArtDeco guide or design-governance documentation.
- [ ] 2.2 Add the route-level E2E hook standard to the page review checklist or verification guide.
- [ ] 2.3 Update the impeccable line summary to point future route craft work at this standard.
- [ ] 2.4 Keep documentation changes free of router, API, shared component, and page-source mutations unless separately approved.

## 3. Optional Page Alignment After Separate Approval

- [ ] 3.1 Select one low-risk route to adopt the hook standard.
- [ ] 3.2 Add failing route-level E2E assertions before page implementation.
- [ ] 3.3 Implement only the approved route-local hook and grammar alignment.
- [ ] 3.4 Verify with targeted E2E, ArtDeco token check, eslint, type-check, and `impeccable --json`.

## 4. Shared Component Extraction Gate

- [ ] 4.1 Draft a separate extraction proposal before creating shared Vue components.
- [ ] 4.2 Define component props, slots, events, state vocabulary, token rules, hook names, migration order, and rollback plan.
- [ ] 4.3 Confirm the candidate does not own API orchestration, route metadata, backend contracts, frontend API clients, or financial row semantics.
