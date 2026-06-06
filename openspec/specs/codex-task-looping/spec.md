# codex-task-looping Specification

## Purpose
TBD - created by archiving change add-codex-ralph-loop-plugin. Update Purpose after archive.
## Requirements
### Requirement: Repo-Local Codex Task Loop Plugin

The repository SHALL provide a repo-local Codex plugin that approximates Ralph-style task looping without depending on a stop-hook auto re-entry mechanism.

#### Scenario: Operator installs or inspects the plugin

- **WHEN** an operator inspects the repo-local plugin directory
- **THEN** they find a `plugins/ralph-loop/.codex-plugin/plugin.json` manifest
- **AND** the manifest describes a local plugin focused on iterative single-task execution

### Requirement: Loop State Must Be Persistable

The plugin SHALL provide a CLI that can create and update a persistent loop state file for one task.

#### Scenario: Initialize a new task loop

- **WHEN** the operator runs the loop CLI with the `init` subcommand
- **THEN** the command creates a loop state file
- **AND** the state captures the task, goal, completion token, status, and max-pass budget

#### Scenario: Record another pass

- **WHEN** the operator runs the loop CLI with the `record` subcommand
- **THEN** the state file appends a new pass entry
- **AND** the state transitions to `active`, `blocked`, `completed`, or `stopped` according to the provided flags and pass budget

### Requirement: Continuation Prompt Must Be Derivable

The plugin SHALL provide a way to derive the next continuation prompt from the saved loop state.

#### Scenario: Generate the next prompt

- **WHEN** the operator runs the loop CLI with the `prompt` subcommand
- **THEN** the command prints a continuation prompt that includes the task, goal, loop status, pass usage, and latest progress

### Requirement: Skill Must State The Limitation Explicitly

The plugin SHALL document that the implementation is an approximation rather than a true stop-hook loop.

#### Scenario: User invokes the Ralph loop skill

- **WHEN** the user invokes `$ralph-loop`
- **THEN** the skill explains that Codex does not expose Claude-style stop-hook auto re-entry
- **AND** it uses explicit passes and persisted state as the supported substitute
