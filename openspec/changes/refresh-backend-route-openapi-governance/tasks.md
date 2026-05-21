# Tasks: Refresh Backend Route/OpenAPI Governance

## 0. Proposal Preparation

- [x] Create OpenSpec proposal, design note, task list, and architecture
  governance spec delta.
- [x] Link D2.3 planning evidence, route/OpenAPI/probe refresh evidence, issue
  `#92` next-lane selection evidence, and steward tree context.
- [x] Keep this change proposal-only and explicitly exclude backend source,
  route behavior, OpenAPI schema, generated client, and test edits.
- [ ] Obtain human approval for this OpenSpec change before starting any
  route/OpenAPI governance execution tasks below.

## 1. Evidence Freshness Gate

- [ ] Refresh route table against the execution branch and record total routes,
  schema-visible routes, hidden runtime routes, endpoint module count, duplicate
  path/method entries, generated timestamp, git head, and stale-if-head-mismatch
  policy.
- [ ] Refresh `app.openapi()` and record path count, operation count, schema
  count, duplicate operationId warnings, warning count, generated timestamp, git
  head, and stale-if-head-mismatch policy.
- [ ] Refresh probe consumer matrix across `.github/workflows/`, `config/`,
  `scripts/`, Docker/PM2/package config, and any approved additional probe
  directories.
- [ ] Stop and return to review if `app.main` import, route table generation, or
  OpenAPI generation fails.

## 2. Route Ownership Classification

- [ ] Classify D2.3 trading candidates by endpoint module, path group,
  schema-exposure state, ownership class, consumer surface, and follow-up lane.
- [ ] Treat `/api/v1/advanced-analysis/trading-signals` as trading-adjacent until
  a later accepted owner decision says otherwise.
- [ ] Classify `/metrics` GET duplicate path/method as a control-plane taxonomy
  item before any schema or runtime route change.
- [ ] Keep backup and recovery routes in the D2.4 ownership lane unless a later
  accepted decision explicitly pulls a narrow item into this change.
- [ ] Keep health/readiness/status/OpenAPI-docs/probe-facing routes in the D2.5
  docs/probe stabilization lane unless a later accepted decision explicitly
  pulls a narrow item into this change.

## 3. Consumer Contract Acceptance

- [ ] For each candidate route group, record path, method, query parameters,
  request body, response shape, caller parser, OpenAPI examples, frontend/test
  consumers, and minimum regression checks.
- [ ] Distinguish runtime route existence from OpenAPI schema exposure for every
  compatibility route or shim.
- [ ] Record explicit exit conditions for keep, hide-from-schema, document,
  migrate, or retire decisions.

## 4. Decision Package

- [ ] Produce a route/OpenAPI governance decision package that maps each
  candidate route group to one of: no action, docs-only, evidence-only,
  dedicated implementation proposal, D2.4 backup ownership, D2.5 control-plane
  docs stabilization, or D2.6 stateful gate approval.
- [ ] Update the codebase-map task tree after the decision package is reviewed.
- [ ] Do not create implementation issues or edit source until the accepted
  decision package identifies the lane, owner, write scope, tests, and rollback
  plan.
