# B4.014 Mainline Runtime Usability Strategic Pivot

Date: 2026-06-24
Program: artdeco-web-design-governance
Mode: strategic governance pivot
Source edits authorized: false

## Decision

The project mainline is reset to runtime usability for the A-share quant system.

All remaining B4.012 residual governance work is frozen as backlog-hold. The completed B4.012 evidence remains useful as a debt map and boundary record, but it must not continue to consume active execution capacity while the quant system runtime mainline is not proven usable.

## Permanent Execution Rules

1. If the program cannot run end-to-end, all detail optimization is prohibited.
2. If pages white-screen, crash, or core APIs return 500, all governance repair work is paused.
3. FUNCTION_TREE may have only one active business mainline at a time.
4. Every implementation package must improve business usability: page access, API 200 recovery, data-chain continuity, quant workflow execution, E2E business smoke, or a real user workflow.
5. Governance debt is inventory-only until the mainline is stable.

## B4.012 Freeze Scope

The active B4.012 governance nodes are moved to a backlog-hold blocker state using the legal FUNCTION_TREE `blocked` status.

Blocked reason:

`backlog-hold: mainline runtime usability is not proven; B4.012 governance repair is forbidden until the A-share quant runtime mainline is stable.`

Closed B4.012 nodes are not reopened or modified.

## New Mainline

New mainline:

`B4.014 mainline A-share quant runtime usability recovery`

First execution node:

`B4.014-M0 A-share quant runtime truth audit`

M0 is read-only and focuses only on runtime business usability:

- backend service startup, port, and health status
- frontend service startup and rendering status
- PM2 backend/frontend status
- eight core business route availability
- core API response status distribution
- OpenStock to MyStocks data-consumption boundary and integration breakpoints
- fatal browser console/runtime errors
- P0/P1 runtime blocker list

## Non-Goals

This pivot does not authorize:

- source/runtime edits
- test edits
- docs cleanup
- OpenSpec edits
- repository hygiene repairs
- directory normalization
- B4.012 governance continuation
- OpenStock provider/runtime development inside `mystocks_spec`
