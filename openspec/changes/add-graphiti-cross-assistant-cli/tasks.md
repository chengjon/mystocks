## 1. Specification

- [x] 1.1 Modify `agent-memory-workflow` to define a canonical shared Graphiti CLI entrypoint.
- [x] 1.2 Modify `agent-memory-workflow` to distinguish Mongo-backed scoped preflight from generic Graphiti memory operations.
- [x] 1.3 Modify `agent-memory-workflow` to require auditable Graphiti write metadata for explicit memory recording.

## 2. CLI Contract

- [x] 2.1 Add a shared Graphiti command surface to the current transitional collaboration CLI.
- [x] 2.2 Add explicit subcommands for scoped preflight and generic memory recording/search.
- [x] 2.3 Keep the command contract compatible with future `maestroctl.py` adoption.

## 3. Service Layer

- [x] 3.1 Extend the shared Graphiti service layer to support generic memory operations without Mongo work-item lookup.
- [x] 3.2 Preserve Mongo-backed scope/context derivation for scoped preflight.
- [x] 3.3 Return `episode_uuid`, `group_id`, ingest status, and timing metadata from explicit write flows.

## 4. Assistant Wrappers

- [x] 4.1 Refactor assistant-specific wrappers/hooks to call the shared CLI instead of embedding command assembly logic.
- [x] 4.2 Treat prompt markers such as `@graphiti` as optional wrapper sugar rather than the primary interface.
- [x] 4.3 Document how non-Claude assistants invoke the same CLI directly.

## 5. Verification

- [x] 5.1 Add unit tests for scoped preflight command behavior.
- [x] 5.2 Add unit tests for generic remember/search command behavior.
- [x] 5.3 Add wrapper tests proving assistant-specific integrations delegate to the shared CLI.
- [x] 5.4 Validate the OpenSpec change with `openspec validate add-graphiti-cross-assistant-cli --strict`.
