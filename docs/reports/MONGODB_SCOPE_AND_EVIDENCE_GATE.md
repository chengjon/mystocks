# MongoDB Scope And Evidence Gate

> Date: 2026-03-12
> Status: Active governance baseline
> Scope: MongoDB usage boundary for MyStocks

## 1. Current Position

MongoDB is **not** a core production data dependency for MyStocks.

Current system baseline remains:

- `TDengine`: primary time-series store
- `PostgreSQL`: primary relational / transactional store
- `Redis`: cache / queue / runtime coordination
- `MongoDB`: optional document-oriented capability, reserved for evidence-backed use only

MongoDB is currently treated as:

- `optional infrastructure`
- `non-blocking for backend readiness`
- `not approved for core quant data paths`

## 2. Why MongoDB Was Considered

MongoDB was originally considered because it is convenient for:

- storing raw JSON payloads
- handling variable / evolving schema
- persisting document-style artifacts without heavy schema migration cost

That rationale is valid in principle, but it is not by itself sufficient to justify active adoption in this project.

## 3. Current Reality

At this time, the repository does **not** provide strong evidence that MongoDB is required for any active business capability.

Specifically:

- there is no confirmed core feature that currently depends on MongoDB for correctness
- there is no established production data flow whose primary artifact is a Mongo-backed document set
- there is no approved feature specification that requires MongoDB over PostgreSQL JSONB or existing storage paths

Therefore MongoDB must remain a reserved option, not an assumed implementation target.

## 4. Allowed Positioning

MongoDB may be considered only for document-oriented scenarios such as:

- raw third-party JSON payload archiving
- audit / event documents
- strategy artifacts with highly variable schema
- metadata or search-oriented document collections

Even in those cases, MongoDB is only a candidate, not the default answer.

## 5. Disallowed Positioning

MongoDB must **not** be treated as:

- a replacement for TDengine time-series storage
- a replacement for PostgreSQL relational or transactional storage
- a default sink for “misc data”
- a silent dependency added to backend startup or readiness
- a fallback chosen only because schema design has not been done

## 6. Evidence Gate

MongoDB can only move from `reserved optional capability` to `approved active capability` when at least one of the following is true:

1. A concrete feature produces durable JSON-first artifacts that must be preserved with minimal transformation.
2. The target data has high schema volatility and PostgreSQL JSONB is shown to be materially worse for the required access pattern.
3. The access pattern is document retrieval / filtering / metadata search rather than relational joins or time-series scans.
4. A reviewed implementation note explains why existing TDengine / PostgreSQL / Redis paths are insufficient.

If none of those conditions are met, MongoDB should not be adopted.

## 7. Approval Checklist

Before any new Mongo-backed feature is implemented, the proposer must answer:

1. What exact artifact will MongoDB store?
2. Why is the artifact document-oriented?
3. Why is PostgreSQL JSONB not sufficient?
4. Is the feature optional or core-runtime-required?
5. What is the retention policy?
6. What is the backup / restore plan?
7. What is the migration / rollback plan if Mongo usage is removed later?

If these answers are incomplete, the proposal is not ready.

## 8. Functional Tree Status

For governance purposes, MongoDB should currently be classified as:

- `功能节点`: infrastructure / optional document store
- `状态`: 待证据支持
- `当前结论`: 保留，不下线；但也不视为已启用业务能力

This means:

- do not remove Mongo blindly
- do not expand Mongo usage casually
- do not describe Mongo as an active business module unless evidence appears

## 9. Development Rule

Going forward:

- new code must not introduce MongoDB as a hard dependency without explicit approval
- readiness checks may report Mongo status, but Mongo must remain non-blocking by default
- docs and deployment assets must describe Mongo as optional unless a later approved feature changes that status

## 10. Recommended Outcome

The project should treat MongoDB as a **kept but gated capability**.

That is the correct middle position:

- better than deleting it without certainty
- better than inventing unsupported business usage for it
- consistent with the actual evidence currently present in the repository
