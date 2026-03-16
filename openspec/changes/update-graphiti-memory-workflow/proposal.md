# Change: Replace Apifox MCP with Graphiti MCP for agent memory workflows

## Why

The repository currently retains a legacy `apifox-api-docs` MCP configuration while project-level agent workflows have shifted toward MongoDB for coordination state and GitNexus for code intelligence. Graphiti MCP is already deployed externally and should become the dedicated memory layer for main/worker CLI collaboration, handoff recall, and fact retrieval.

Without an explicit project decision, switching the MCP server alone would leave the Graphiti/Mongo boundary undefined and create a risk of dual sources of truth for task state.

## What Changes

- Remove the remaining Apifox MCP configuration from project MCP config files.
- Add Graphiti MCP to the active project MCP configuration using the verified HTTP endpoint.
- Define project-level rules for when agents should use Graphiti MCP versus Mongo coordination state.
- Document recommended `group_id` naming and the initial call sequence for main/worker CLI usage.

## Impact

- Affected specs: `agent-memory-workflow`
- Affected code/config:
  - `.mcp.json`
  - `config/.mcp.json`
  - `docs/guides/MONGO_MULTICLI_COORDINATION_GUIDE.md`
  - `docs/guides/GRAPHITI_MCP_WORKFLOW.md`
