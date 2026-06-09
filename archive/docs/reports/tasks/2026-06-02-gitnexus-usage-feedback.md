# GitNexus Usage Feedback

Date: 2026-06-02

Context: feedback from the ArtDeco SCSS file-size guard line, especially repeated use of `impact`, local `gitnexus analyze`, and `detect_changes` while splitting large SCSS files without changing router, API contracts, frontend API client, Vue runtime logic, or shared components.

## Summary

GitNexus was useful as a governance and blast-radius guard, especially for proving that a style-only change had low graph impact before edit and before commit. The strongest value was not "finding the code" in this line, but creating repeatable evidence: target file, risk level, affected process count, changed file count, selected repo path, and worktree resolution.

The main weakness was index freshness reporting. Local `gitnexus analyze` completed successfully after each staged batch, but the GitNexus MCP `detect_changes` metadata repeatedly reported a stale `indexed_commit`. That makes the evidence harder to trust and forces the agent to explain an exception every time.

## What Worked Well

### 1. Pre-change impact was fast and useful

For SCSS file targets such as:

- `web/frontend/src/styles/bloomberg-terminal-override.scss`
- `web/frontend/src/styles/element-plus-artdeco.scss`
- `web/frontend/src/styles/pro-fintech-optimization.scss`
- `web/frontend/src/styles/element-plus-override.scss`

`impact` returned a concise low-risk summary:

- target file resolved correctly
- upstream direction was supported
- direct dependents: `0`
- affected processes: `0`
- modules affected: `0`
- risk: `LOW`

This is good evidence for small scoped edits. It also helps distinguish "visual/style asset split" from route, API, or runtime behavior changes.

### 2. `detect_changes` was useful as a final staged gate

After staging only the allow-listed files, `detect_changes(scope: "staged")` provided a clean final check:

- changed file count
- changed symbol count
- affected process count
- risk level
- selected repo and diff path metadata
- worktree path resolution

For this line, it consistently confirmed `low` risk and `0` affected processes, which is exactly the level of evidence needed before committing mechanical SCSS splits.

### 3. `cwd` / worktree metadata is valuable

The metadata showing:

- `git_repo_path`
- `git_diff_path`
- `process_cwd`
- `path_resolution`
- `selected_repo`
- `repo_path`
- `storage_path`

is useful in a dirty multi-worktree environment. It makes it easier to prove that the analysis targeted `/opt/claude/mystocks_spec`, not another checkout or default directory.

### 4. Local CLI analyze is important

The user explicitly asked to use local:

```bash
gitnexus analyze
```

instead of:

```bash
npx gitnexus analyze
```

That is the right rule for this repository because local GitNexus has user-modified functionality. The feedback here assumes local CLI is the canonical analyzer for this workspace.

## Problems Observed

### P0: MCP stale metadata after successful local analyze

Observed pattern:

1. Run local `gitnexus analyze --index-only --max-file-size 64 --worker-timeout 10`.
2. CLI reports repository indexed successfully.
3. Run GitNexus MCP `detect_changes(scope: "staged")`.
4. MCP returns useful risk summary, but metadata still reports:

```text
stale: true
stale_reason: current_commit_differs_from_indexed_commit
indexed_commit: 4beaff...
current_commit: <current HEAD>
```

This creates a trust problem. If local analyze succeeded, the MCP should either:

- see the refreshed index, or
- explain that it is reading a different index namespace/path, or
- distinguish "HEAD changed because staged diff is uncommitted" from "graph index is stale for the files being analyzed".

Current behavior makes every report carry a caveat: "local analyze succeeded, but MCP metadata still says stale."

### P1: Style-only changes are under-explained

For SCSS split commits, `detect_changes` often reported changed symbols mostly from the Markdown report sections, while the actual SCSS partials appeared primarily through changed file counts.

For style assets, it would be more useful to expose:

- changed style files
- added Sass partials
- facade file that imports the partials
- Sass/CSS import relationships
- Vite/main entry import path, if present
- whether the style file is actively imported by a runtime entry

Right now, a style-only change can look like "docs changed" in the symbol list even when the meaningful artifact is a SCSS facade/partial split.

### P1: Analyze latency is high for repeated staged micro-commits

During this line, local analyze commonly took around 60-125 seconds. It also repeatedly printed:

```text
Skipped 836 large files (>64KB)
```

For a staged SCSS-only split, this feels heavier than necessary.

Useful optimization options:

- `gitnexus analyze --staged-only`
- `gitnexus analyze --changed-only`
- `gitnexus analyze --files <path...>`
- reuse prior large-file skip scan without reprinting it every run
- return a short "index already current for staged files" result when applicable

### P2: Optional grammar warning is noisy

Every analyze printed the optional `.proto` grammar warning:

```text
optional grammar "tree-sitter-proto" is unavailable
```

This is technically valid, but irrelevant for SCSS-only work. It should be downgraded or summarized when the changed file set has no `.proto` files.

Suggested behavior:

- show once per repo/session
- suppress unless `--verbose`
- or print: `optional .proto parser unavailable; no .proto files in changed set`

### P2: Risk rationale could be more explicit

`risk_level: low` is useful, but the tool could add a short machine-readable rationale:

```json
{
  "risk_rationale": [
    "changed files are style/docs/governance only",
    "no changed symbol participates in indexed processes",
    "no upstream callers detected"
  ]
}
```

This would reduce repeated manual explanation in final reports.

### P2: File-level target syntax is useful but slightly opaque

The working target format:

```text
File:web/frontend/src/styles/element-plus-artdeco.scss
```

is clear once known, but could be easier to discover. Tool help could show first-class examples for non-code assets:

- SCSS file
- Markdown file
- route file
- API handler file
- Vue SFC

## Improvement Suggestions

### 1. Add an explicit index freshness command

Suggested tool/CLI:

```bash
gitnexus status --json
```

Useful fields:

```json
{
  "repo": "mystocks",
  "repo_path": "/opt/claude/mystocks_spec",
  "index_path": "...",
  "indexed_commit": "...",
  "current_commit": "...",
  "dirty": true,
  "staged_files": 10,
  "unstaged_files": 300,
  "index_updated_at": "2026-06-02T...",
  "fresh_for_staged_diff": true,
  "fresh_for_head": true
}
```

Important distinction: a worktree can be dirty while the index is still fresh enough for staged diff analysis.

### 2. Make MCP and local CLI index paths explicit and consistent

If local CLI and MCP use different storage/index paths, both should expose that clearly.

Suggested fields in `detect_changes.metadata`:

- `analyzer_source`: `mcp` / `local-cli-compatible`
- `last_analyze_command`
- `last_analyze_exit_code`
- `last_analyze_at`
- `index_generation_id`
- `index_path`
- `index_matches_local_cli: true|false|unknown`

This would make stale warnings actionable instead of ambiguous.

### 3. Add style/import graph support

For frontend repositories, GitNexus could extract relationships from:

- Sass `@use`
- Sass `@import`
- CSS `@import`
- TypeScript/Vue style imports
- Vite entry imports
- Vue SFC `<style src="">`

Then SCSS changes could show:

```text
element-plus-artdeco.scss imports:
- element-plus-artdeco.variables.scss
- element-plus-artdeco.core-components.scss

Runtime consumers:
- main-standard.ts imports element-plus-override.scss
- no direct runtime import detected for bloomberg-terminal-override.scss
```

That would be very useful for design-system governance and for deciding whether a style file is active, legacy, opt-in, or dead.

### 4. Add `detect_changes` file classification

Suggested output:

```json
{
  "changed_file_classes": {
    "style": 6,
    "docs": 1,
    "governance": 3,
    "source": 0,
    "api_contract": 0,
    "router": 0
  }
}
```

This directly supports project rules such as:

- no router change
- no API contract change
- no frontend API client change
- no runtime logic change

### 5. Add governance-friendly summary output

For Function Tree closeout, a compact evidence block would help:

```json
{
  "gate_summary": {
    "risk": "LOW",
    "affected_processes": 0,
    "changed_files": 10,
    "forbidden_file_classes": [],
    "stale": false,
    "warnings": []
  }
}
```

This could be copied directly into task reports.

### 6. Better handling for large dirty worktrees

This repo often has many unrelated dirty files. GitNexus already supports `scope: "staged"`, which is good. It could go further:

- warn if staged files include unexpected categories
- ignore unstaged noise in summary mode
- include `unstaged_ignored_count`
- explicitly state: `analysis limited to staged diff`

This would reduce uncertainty in long-running multi-agent worktrees.

## Suggested Priority

| Priority | Recommendation | Why |
| --- | --- | --- |
| P0 | Fix or clarify MCP stale metadata after successful local analyze | Current caveat weakens every final gate report |
| P1 | Add staged/changed/file-scoped analyze mode | Repeated style micro-commits currently spend too much time indexing unrelated files |
| P1 | Add Sass/CSS import graph extraction | Frontend design-system governance needs active style dependency visibility |
| P1 | Add file classification to `detect_changes` | Directly supports no-router/no-API/no-client policy gates |
| P2 | Suppress irrelevant optional grammar warnings | Reduces noise for non-proto work |
| P2 | Add risk rationale | Makes LOW/HIGH risk easier to trust and report |

## Practical Usage Guidance For This Repo

Recommended agent pattern:

1. Run `impact` before editing a file or symbol.
2. For local index refresh, use local CLI:

   ```bash
   gitnexus analyze --index-only --max-file-size 64 --worker-timeout 10
   ```

3. Do not use `npx gitnexus analyze` in this repo unless the user explicitly changes the rule.
4. Run `detect_changes(scope: "staged", cwd: "/opt/claude/mystocks_spec")` before commit.
5. Treat `risk_level` and `affected_processes` as useful evidence, but also report stale metadata when present.
6. For SCSS work, supplement GitNexus with:
   - exact staged allow-list check
   - SCSS body reconstruction check
   - `git diff --cached --check`
   - ArtDeco token checker
   - `npm run build:no-types`

## Bottom Line

GitNexus is already valuable as a safety and governance layer. It works especially well when paired with staged-only workflows and Function Tree closeout. The biggest improvement would be making index freshness unambiguous and adding first-class frontend style/import awareness. Those two changes would turn GitNexus from a mostly code-symbol blast-radius tool into a stronger design-system governance tool for this repository.
