# frontend-routing Delta: refactor-entry-consolidation

## MODIFIED Requirements

### Requirement: Single Entry Point Architecture

The frontend SHALL use exactly one active entry point (`main-standard.ts`) that includes all production capabilities: component registration, security initialization, error handling, PWA registration, session restore, version negotiation, and debug access.

The entry point SHALL follow a non-blocking async pattern: the app mounts synchronously (UI renders immediately), then async initialization (security, PWA, session, version) runs after mount without blocking rendering.

Legacy entry points (`main.js`, `main.js.backup`) SHALL be archived in `_entry-archive/` with a rollback README, not deleted.

#### Scenario: Production Boot Sequence
- **WHEN** the application starts via `main-standard.ts`
- **THEN** Vue app mounts synchronously with all component registrations
- **AND** the UI renders before async initialization completes
- **AND** security init runs with a 2-second timeout race
- **AND** PWA service worker registers on window load event
- **AND** session restore runs via dynamic import after security completes
- **AND** version negotiation runs after security completes

#### Scenario: Entry Point Rollback
- **WHEN** a regression is detected in the consolidated entry point
- **THEN** `main.js` can be restored from `_entry-archive/`
- **AND** `index.html` line 67 can be changed back to `/src/main.js`
- **AND** the application boots with the previous behavior

#### Scenario: Error Isolation
- **WHEN** an async initialization step fails (security, PWA, session, version)
- **THEN** the failure is logged with `[MyStocks]` prefix
- **AND** the application continues running (non-blocking)
- **AND** no emoji-based debug logs appear in production

## REMOVED Requirements

### Requirement: Bloomberg Terminal Override Styles

The Bloomberg terminal override styles import is dropped from the entry point. ArtDeco is the current design system; Bloomberg overrides are a legacy layer with no active consumers.
