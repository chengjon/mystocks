# Phase 2 Real Data Integration Plan Review

**Review Date**: 2026-01-02
**Reviewer**: Gemini CLI Agent
**Target Document**: `docs/guides/PHASE_2_REAL_DATA_INTEGRATION_PLAN.md`
**Status**: ✅ **APPROVED** with minor recommendations

---

## 1. Overall Assessment

The **Phase 2 Real Data Integration Plan** is exceptionally well-structured, pragmatic, and safe. It correctly identifies the critical path: moving from "plumbing" (API standardization) to "water" (data flow) without overwhelming the system.

### Key Strengths 🌟
*   **Risk Mitigation**: The decision to start with **Read-Only** modules (Industry/Concept) is the perfect strategy to validate the pipeline without risking data corruption.
*   **Verification Layering**: The three-tier verification approach (`Database SQL` -> `API curl` -> `Frontend Browser`) ensures issues are isolated immediately at their source.
*   **Clear Success Metrics**: Each sub-phase has quantifiable success criteria (e.g., "> 50 industries", "HTTP 200").
*   **Rollback Strategy**: The inclusion of specific rollback commands (`USE_MOCK_DATA=true`) provides a safety net for development continuity.

---

## 2. Technical Recommendations & Refinements

While the plan is solid, I recommend the following refinements to ensure smoother execution:

### 2.1 Data Integrity Checks (Phase 2.1 & 2.2)
*   **Orphaned Data**: When verifying Industries/Concepts, add a check to ensure `stocks_basic` actually references these valid industry codes.
    ```sql
    -- Integrity Check Example
    SELECT count(*) FROM stocks_basic WHERE industry NOT IN (SELECT industry_name FROM stock_industries);
    ```
    *Why*: Prevents frontend "blank" filters where a stock exists but doesn't appear under its listed industry.

### 2.2 K-Line Performance (Phase 2.3)
*   **Large Dataset Handling**: Fetching full K-line history can be heavy.
    *   *Recommendation*: Ensure the backend enforces a default `limit` or strict `start_date` if none is provided, to prevent accidental "SELECT ALL" queries that could time out the frontend.
    *   *Frontend Optimization*: Verify that the Chart component handles large arrays (e.g., >2000 points) gracefully, or implement data downsampling for long-term views.

### 2.3 Hybrid Mode Clarification
*   **Mock vs. Real vs. Hybrid**: The plan mentions `USE_MOCK_DATA=true` as a binary switch. However, some backend code docstrings mention a "Hybrid" mode.
    *   *Action*: Clarify in the implementation if we are supporting a mixed state (e.g., Real stock list but Mock K-lines) or if it's strictly one or the other. A strict binary switch is recommended for Phase 2 to reduce complexity.

### 2.4 Environment Security
*   **Secrets Management**: Ensure `POSTGRESQL_PASSWORD` and other sensitive keys are not just present but correctly loaded by `pydantic`.
    *   *Check*: Run a quick script to verify database connectivity *before* starting the server to avoid "CrashLoopBackOff" scenarios in PM2.

---

## 3. Strategic Endorsement

I **strongly endorse** proceeding immediately with **Phase 2.1 (Industry & Concept Lists)**.

*   **Rationale**: It validates the entire DB-to-Frontend stack with minimal complexity.
*   **Impact**: Success here proves the architecture works; failure here is easy to debug.

### Proposed Immediate Action
Execute **Phase 2.1** steps as defined in the plan:
1.  Verify DB Connectivity.
2.  Switch `.env` to `USE_MOCK_DATA=false`.
3.  Test Industry/Concept endpoints.

**Verdict**: The plan is **Ready for Execution**. 🚀
