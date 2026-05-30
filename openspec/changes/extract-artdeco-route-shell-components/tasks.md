## 1. Proposal Validation

- [x] 1.1 Review the completed `standardize-artdeco-route-grammar` pilot evidence.
- [x] 1.2 Draft the extraction proposal, design note, and spec delta.
- [x] 1.3 Run `openspec validate extract-artdeco-route-shell-components --strict`.
- [ ] 1.4 Present the proposal for approval before any shared Vue component implementation.

## 2. Contract Definition After Approval

- [ ] 2.1 Define final component names and ownership boundaries.
- [ ] 2.2 Define props, slots, events, hook passthrough, token rules, and supported runtime vocabulary.
- [ ] 2.3 Choose the first low-risk migrated route and write the route migration report template.

## 3. Implementation After Separate Approval

- [ ] 3.1 Add focused E2E coverage before the first component migration.
- [ ] 3.2 Implement one shared shell surface only.
- [ ] 3.3 Migrate one route slice while preserving existing route-level hooks and copy.
- [ ] 3.4 Verify with focused E2E, ArtDeco token check, `npx impeccable --json`, eslint, type-check, PM2 status, OpenSpec validation, and GitNexus staged scope gate.
- [ ] 3.5 Stop after the first verified migrated route and request follow-up approval before broader rollout.
