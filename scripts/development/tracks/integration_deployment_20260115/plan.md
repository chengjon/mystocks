# Track Plan: Frontend/Backend Integration and Deployment

This plan outlines the steps to integrate the frontend and backend, verify API connections, and deploy the MyStocks application.
Based on: `docs/guides/前后端整合与部署完整方案.md`

## Phase 1: Environment Configuration Unification [Est: 2h]

### Goal: Standardize frontend and backend environment configurations.

- [ ] Task: Create unified environment configuration files (.env.development, .env.staging, .env.production).
    - [ ] Action: Create files in root directory.
- [ ] Task: Standardize Backend Environment Variables.
    - [ ] Action: Update `web/backend/app/core/config.py` to include DATABASE_URL, JWT_SECRET_KEY, CORS_ORIGINS, FRONTEND_URL.
- [ ] Task: Standardize Frontend Environment Variables.
    - [ ] Action: Update `web/frontend/.env` to include VITE_API_BASE_URL, VITE_WS_BASE_URL, VITE_APP_TITLE.
- [ ] Task: Verify Configuration Loading.
    - [ ] Action: Verify backend loads settings correctly.
    - [ ] Action: Verify frontend loads VITE_ variables.
- [ ] Task: Conductor - User Manual Verification 'Environment Configuration'

## Phase 2: Frontend Routing Integration Test [Est: 3h]

### Goal: Verify all page routing configurations.

- [ ] Task: Check Route Integrity (`web/frontend/src/router/index.ts`).
- [ ] Task: Test Route Transitions (Manual or E2E).
- [ ] Task: Configure 404 Page.
- [ ] Task: Verify Route Guards (Auth/Permissions).
- [ ] Task: Conductor - User Manual Verification 'Frontend Routing'

## Phase 3: API Connection Integrity Verification [Est: 8h]

### Goal: Verify all frontend API calls against backend endpoints.

- [ ] Task: Create API Connection Checklist (Map pages to endpoints).
- [ ] Task: Verify Core APIs (Auth, Market, Strategy, Risk).
- [ ] Task: Test API Call Flow (Login -> Token -> Request).
- [ ] Task: Verify Error Handling (Network, Timeout, 401/403/500).
- [ ] Task: Switch from Mock to Real Data (Remove mock dependencies).
- [ ] Task: Conductor - User Manual Verification 'API Connection'

## Phase 4: Build Configuration Optimization [Est: 4h]

### Goal: Optimize frontend build for performance.

- [ ] Task: Implement Code Splitting Strategy (vite.config.ts).
- [ ] Task: Optimize Route Lazy Loading.
- [ ] Task: Configure Resource Compression (Terser).
- [ ] Task: Inject Environment Variables.
- [ ] Task: Analyze Build Artifacts (Bundle Visualizer).
- [ ] Task: Conductor - User Manual Verification 'Build Optimization'

## Phase 5: Local Run Test [Est: 2h]

### Goal: Verify full system integration locally.

- [ ] Task: Start Backend Service (with real env).
- [ ] Task: Start Frontend Service (dev mode).
- [ ] Task: Perform Full Functionality Test (Login, Dashboard, Market, Strategy).
- [ ] Task: Check Console/Logs for Errors.
- [ ] Task: Conductor - User Manual Verification 'Local Run Test'

## Phase 6: Packaging and Building [Est: 3h]

### Goal: Generate production-ready artifacts.

- [ ] Task: Build Frontend (`npm run build`).
- [ ] Task: Prepare Backend (requirements.txt, start.sh, Dockerfile).
- [ ] Task: Configure Static File Serving (FastAPI mount).
- [ ] Task: Verify Build Artifacts (dist/ check).
- [ ] Task: Conductor - User Manual Verification 'Packaging'

## Phase 7: Deployment Scheme Design [Est: 4h]

### Goal: Provide deployment options.

- [ ] Task: Design Traditional Deployment Scheme (Script-based).
- [ ] Task: Design Docker Deployment Scheme (docker-compose).
- [ ] Task: Design Cloud Service Deployment Scheme (Architecture).
- [ ] Task: Create Deployment Documentation.
- [ ] Task: Conductor - User Manual Verification 'Deployment Design'

## Phase 8: Documentation [Est: 3h]

### Goal: Create user and operation manuals.

- [ ] Task: Write Quick Start Guide (`QUICKSTART.md`).
- [ ] Task: Write Deployment Guide (`DEPLOYMENT.md`).
- [ ] Task: Write API Documentation (`API.md`).
- [ ] Task: Write Troubleshooting Guide (`TROUBLESHOOTING.md`).
- [ ] Task: Conductor - User Manual Verification 'Documentation'

## Phase 9: Final Verification and Delivery [Est: 2h]

### Goal: Final sign-off.

- [ ] Task: Full Regression Test.
- [ ] Task: Performance Benchmark (Lighthouse).
- [ ] Task: Security Check (Secrets, CORS, CSRF).
- [ ] Task: Final Delivery Checklist.
- [ ] Task: Conductor - User Manual Verification 'Final Delivery'
