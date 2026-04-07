# Redis / Mongo Runtime Config Requirements

> **历史文档说明**:
> 本文件是某阶段的历史文档、过程记录或专题材料，不是当前基线、当前系统总览或仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现、验证结果及主线文档一并核对。
>
> 文内描述、背景、结论和上下文如未重新复核，应视为历史快照，不得直接当作当前事实。


> Date: 2026-03-12
> Status: Draft for developer review
> Scope: Runtime configuration governance only
> Constraint: Do not change the currently running `mystocks-redis` and `mystocks-mongodb` instances in this phase

## 1. Current Baseline

Confirmed runtime state:

- `mystocks-redis` is running on port `6379`
- `redis.ping() == True`
- `mystocks-mongodb` is running on port `27017`
- `db.admin.command('ping') == 1.0`

This proposal does **not** request changing those live settings.
Its purpose is to define the governance requirements that future code, docs, and deployment assets must follow.

## 2. Approaches Considered

### Option A: Keep Current State And Only Document It
Pros:
- No immediate engineering cost
- No runtime risk

Cons:
- Existing Redis DB role ambiguity remains
- Future developers will keep hardcoding incompatible defaults
- Mongo may be introduced into core paths without an explicit boundary

### Option B: Governance-First, No Runtime Mutation (Recommended)
Pros:
- Lowest risk path
- Respects the current running Redis/Mongo instances
- Creates a clear contract before wider refactors
- Allows phased migration from legacy env vars and ad hoc defaults

Cons:
- Requires short-term discipline and review overhead
- Some duplication remains until migration work is scheduled

### Option C: Immediate Standardization Across All Code Paths
Pros:
- Fast convergence if done perfectly

Cons:
- Highest regression risk
- Likely to break monitoring, tooling, or Celery assumptions
- Violates the current constraint of not changing active Redis/Mongo config

## 3. Recommendation

Adopt **Option B**.

That means:
- Freeze the currently running Redis and Mongo infrastructure settings
- Approve an explicit role matrix and environment-variable contract
- Require new code to follow the approved contract
- Migrate legacy code incrementally only after review

## 4. Redis Requirements

### R-1. Redis Must Use An Explicit Logical Role Matrix
The project must stop treating a single `REDIS_DB` value as universally correct.

Approved baseline roles for review:

| Role | Default DB | Purpose |
|------|------------|---------|
| `app_cache` | `1` | Main backend cache, app-level Redis access |
| `monitoring_events` | `0` | Monitoring queue / publisher-worker flow |
| `tooling_maintenance` | `0` | Database utility scripts, maintenance helpers |
| `celery_broker` | `0` | Celery broker |
| `celery_result` | `1` | Celery result backend |

Requirement:
- Any new Redis usage must declare its logical role before implementation.
- Any proposal to change a role's DB assignment must include impact and rollback notes.

### R-2. Redis Environment Variables Must Be Role-Aware
Recommended target variables:

- `REDIS_HOST`
- `REDIS_PORT`
- `REDIS_PASSWORD`
- `REDIS_APP_CACHE_DB`
- `REDIS_MONITORING_DB`
- `REDIS_TOOLING_DB`
- `REDIS_CELERY_BROKER_DB`
- `REDIS_CELERY_RESULT_DB`

Compatibility rule:
- Legacy `REDIS_DB` may remain as a temporary fallback for legacy code.
- New or migrated code must prefer the role-specific variable.

### R-3. Redis Variable Precedence Must Be Deterministic
Required precedence order:

1. Role-specific variable
2. Legacy `REDIS_DB`
3. Code-local default approved for that role

No code path should silently invent a different default without documentation.

### R-4. Redis Connectivity Contract Must Be Standardized
Every runtime path using Redis must standardize:

- connection timeout
- socket timeout
- decode mode
- connection pool sizing rationale
- authentication handling when password is empty vs set

Minimum requirement:
- Health check must be `redis.ping()` or equivalent
- Failure logs must include the logical role and resolved DB number

### R-5. Redis Usage In Core Runtime Must Be Classified
Each Redis-dependent path must be tagged as one of:

- `core-runtime-required`
- `performance-optional`
- `monitoring-optional`
- `tooling-only`

Policy:
- `monitoring-optional` and `tooling-only` paths must degrade gracefully when Redis is unavailable.
- `core-runtime-required` paths require explicit approval.

### R-6. Redis Documentation Must Match Runtime Reality
Any change to Redis DB assignment, env names, or connection rules must update in the same change:

- runtime config provider docs
- deployment docs
- verification commands
- migration notes

## 5. MongoDB Requirements

### M-1. MongoDB Must Remain Optional By Default
MongoDB must **not** become a required dependency for the main backend startup path unless a separately approved feature explicitly requires it.

Policy:
- No backend readiness gate may fail solely because MongoDB is absent, unless the running feature set has an approved Mongo dependency.
- MongoDB is currently treated as optional infrastructure.

### M-2. MongoDB Must Use A Standard Variable Contract
Recommended target variables:

- `MONGODB_HOST`
- `MONGODB_PORT`
- `MONGODB_ROOT_USERNAME`
- `MONGODB_ROOT_PASSWORD`
- `MONGODB_DATABASE`
- `MONGODB_AUTH_SOURCE` with default `admin`
- Optional derived `MONGODB_URL`

Current runtime baseline to preserve in this phase:
- port `27017`

### M-3. MongoDB Health Check Must Be Standardized
Approved health check style:

```bash
mongosh --quiet --eval "db.adminCommand({ ping: 1 })"
```

Requirements:
- New deployment assets must prefer `mongosh`, not `mongo`
- Health checks must not rely on shell behavior that varies by image version

### M-4. MongoDB Admissible Use Cases Must Be Explicit
MongoDB should only be considered for approved document-oriented or flexible-schema use cases, for example:

- audit/event documents
- raw third-party JSON payload archiving
- strategy artifacts with highly variable schema
- document search or metadata aggregation use cases approved separately

MongoDB must **not** be adopted as a default replacement for:

- TDengine time-series storage
- PostgreSQL relational/transactional storage
- existing core quant data paths without explicit approval

### M-5. MongoDB Security And Operations Requirements
Required controls:

- no hardcoded credentials in committed code
- explicit auth source documentation
- backup/restore procedure documented before production dependency is approved
- container/image version pinning for managed deployment assets
- runtime logs must clearly indicate authentication failures and connectivity failures

## 6. Cross-Cutting Governance Requirements

### G-1. Standard Variables Must Win Over Legacy Aliases
For runtime config providers, standard env names must take precedence over compatibility aliases.

Examples:
- `POSTGRESQL_*` over `DB_POSTGRESQL_*`
- `TDENGINE_*` over `DB_TDENGINE_*`
- future Redis role variables over `REDIS_DB`

### G-2. No Silent Drift Across Deployment Assets
Docker/compose/infra docs/scripts must not silently diverge on:

- ports
- usernames
- default DB numbers
- health-check client commands
- mounted config file paths

### G-3. Review Gate Is Mandatory For Redis/Mongo Scope Changes
A developer must submit a reviewed proposal before changing any of the following:

- Redis role matrix
- Redis DB assignments
- Mongo dependency level (optional -> required)
- Mongo port/credential contract in managed deployment assets
- backend readiness behavior related to Redis/Mongo

### G-4. Verification Commands Must Be Part Of The Contract
Minimum verification commands to keep documented:

```bash
redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" ping
redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" -n "$REDIS_APP_CACHE_DB" ping
redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" -n "$REDIS_MONITORING_DB" ping
mongosh --quiet --eval "db.adminCommand({ ping: 1 })"
```

## 7. Implementation Expectations For Developers

### Phase 1: Governance Approval
- Approve or revise the Redis role matrix
- Approve Mongo optional-boundary policy
- Approve standard variable names and precedence rules

### Phase 2: Config Provider Convergence
- Update config providers to read standard variables first
- Add role-specific Redis variables where justified
- Keep compatibility fallback only where migration is incomplete

### Phase 3: Deployment And Verification Convergence
- Align Docker/infra docs and verification scripts
- Standardize Mongo health check to `mongosh`
- Document which services are allowed to hard-require Redis/Mongo

### Phase 4: Incremental Refactor
- Replace raw `REDIS_DB` usage in role-specific paths
- Remove undocumented defaults
- Keep backward compatibility until migration is signed off

## 8. Explicit Non-Requirements In This Phase

This phase does **not** require:

- changing the live Redis port or DB assignments
- changing the live Mongo port
- making Mongo a core application dependency
- performing a full repository-wide Redis refactor immediately
- replacing TDengine or PostgreSQL with MongoDB

## 9. Reviewer Checklist

Developers reviewing this proposal should explicitly answer:

1. Is the Redis role matrix acceptable as the project baseline?
2. Should `monitoring_events` remain on DB `0`, or does it require a dedicated DB later?
3. Should GPU-related Redis usage remain grouped with tooling on DB `0`, or become its own role?
4. Is MongoDB correctly classified as optional infrastructure at this stage?
5. Are there any approved near-term Mongo-backed features that would require a separate spec?
6. Are the proposed standard variable names acceptable for future code convergence?
7. Is `mongosh` approved as the single health-check client for managed assets?

## 10. Recommended Outcome

Approve this document as the governance baseline, then schedule follow-up implementation work in small, reviewable slices:

- first Redis role variable adoption
- then deployment/doc convergence
- then selective refactors

This keeps the currently running Redis/Mongo instances untouched while preventing future configuration drift.
