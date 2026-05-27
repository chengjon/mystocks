# Track: Route / OpenAPI Governance

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Status: active track summary
- Prepared at: `2026-05-27T21:33:48+08:00`
- Base HEAD checked: `b54e7d043720a8c8bc67ad96f4f7eaad0b23ceba`

Boundary note: this track summary does not authorize route source edits,
OpenAPI exposure changes, compatibility deletion, frontend consumer changes, or
runtime rollout.

## Track Role

Route/OpenAPI governance owns decisions that are not merely file moves:

- canonical route ownership
- compatibility shim status
- route table diff
- OpenAPI path and operation ID exposure
- frontend/test/probe consumer contracts
- control-plane endpoint taxonomy
- response wrapper consistency

## Operating Rule

Do not treat a route migration as closed by path movement alone. Closure requires
consumer-contract parity:

- path
- method
- query parameters
- response shape
- caller parser
- OpenAPI examples or schema exposure
- minimal regression evidence
- explicit delete / retain / runtime-only shim decision

## Relationship To Current Steward Split

The root steward tree no longer carries full route history inline. Current route
governance facts should be placed here or in a dedicated route decision package,
then indexed from `evidence-index.md` and `steward-index.json` when active.

## Next Gates

- Review G2.185 route dependency/provider governance residual decision. It
  classifies active FastAPI providers as route contracts and does not authorize
  route source edits or OpenAPI exposure changes.
- Use this track for future trading route, backup route, control-plane, health,
  status, probe, and compatibility exposure decisions.
- Keep source edits locked until the route owner, OpenAPI exposure policy, and
  consumer matrix are explicit.
