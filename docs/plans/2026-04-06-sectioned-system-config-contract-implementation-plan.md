# Sectioned System-Config Contract Implementation Plan

> **历史计划说明**:
> 本文件记录某次阶段性治理、任务推进或方案落地时的历史执行计划、目标拆解与验证设想，反映的是当时准备推进的方向与范围，而非当前已生效事实。
> 若其内容与现行 `architecture/STANDARDS.md`、当前实现或后续结论不一致，应以 `architecture/STANDARDS.md`、当前实现与最新结论为准。

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the approved `add-sectioned-system-config-contract` change in governed micro-batches, first by composing existing canonical datasource and notification truths, then by adding canonical system-scoped `general` and `security` contracts, and only then retiring local-storage degradation.

**Architecture:** The page-level `SystemSettings` shape stays unified, but ownership remains sectioned. `datasource` continues to use the existing data-source config backend, `notification` continues to use the user-scoped notification preferences backend, and `general`/`security` are added later through new system-scoped APIs under `/api/v1/system`. No composition layer may become a second persistence truth.

**Tech Stack:** FastAPI, Pydantic, Vue 3, Pinia, TypeScript, Vitest, pytest, OpenSpec

---

## File Map

- `web/frontend/src/services/TradingApiManager.types.ts`
  - Expand `SystemSettings` metadata from blanket degraded flags into section ownership/status/evidence metadata.
- `web/frontend/src/services/systemSettingsContract.ts`
  - Build sectioned snapshots, validate allowed write sections, and keep section-level unsupported states explicit.
- `web/frontend/src/services/TradingApiManager.ts`
  - Compose `datasource` and `notification` through their canonical owners and route writes per section.
- `web/frontend/src/api/user.ts`
  - Align frontend notification-preferences endpoints with the backend canonical `/preferences` contract.
- `web/frontend/src/services/__tests__/systemSettingsContract.spec.ts`
  - Frontend contract unit tests for section metadata and write validation.
- `web/frontend/src/services/__tests__/TradingApiManager.system-settings.spec.ts`
  - Frontend composition tests for datasource/notification reads and writes.
- `web/frontend/src/stores/system.ts`
  - Consume richer section metadata without reintroducing local persistence as a second truth.
- `web/frontend/src/views/system/Settings.vue`
  - Replace blanket degraded messaging with section-aware truth messaging when the page is ready to surface the contract.
- `web/backend/app/api/v1/system/__init__.py`
  - Export future system settings router.
- `web/backend/app/api/v1/system/settings.py`
  - New canonical system-scoped `general`/`security` read-write endpoints.
- `web/backend/app/api/v1/router.py`
  - Register the future system settings router under `/api/v1/system`.
- `web/backend/tests/test_health_route_conflicts.py`
  - Extend OpenAPI/route coverage for the new system settings endpoints and existing notification preferences truth.
- `web/backend/tests/test_system_settings_contract.py`
  - New backend tests for section-scoped system settings behavior.

## Execution Order

1. Frontend service-layer truth composition for `datasource` and `notification`
2. Frontend store/page messaging alignment
3. Backend system-scoped `general` contract
4. Backend system-scoped `security` contract
5. Local-storage fallback retirement after section exit criteria pass

## Task 1: Expand Frontend Section Metadata

**Files:**
- Modify: `web/frontend/src/services/TradingApiManager.types.ts`
- Modify: `web/frontend/src/services/systemSettingsContract.ts`
- Test: `web/frontend/src/services/__tests__/systemSettingsContract.spec.ts`

- [ ] **Step 1: Write the failing test for section metadata**

```ts
it('builds section metadata with explicit owner, scope, status, and evidence', () => {
  const snapshot = buildSystemSettingsSnapshot({
    datasource: { providers: ['akshare'] },
    notification: { email_enabled: true },
  })

  expect(snapshot.meta.sections.datasource).toMatchObject({
    scope: 'system',
    owner: 'data-source-config',
    readStatus: 'available',
    writeStatus: 'available',
    evidenceType: 'measured',
  })

  expect(snapshot.meta.sections.notification).toMatchObject({
    scope: 'user',
    owner: 'notification-preferences',
    readStatus: 'available',
    writeStatus: 'available',
    evidenceType: 'measured',
  })

  expect(snapshot.meta.sections.general.readStatus).toBe('unavailable')
  expect(snapshot.meta.sections.security.readStatus).toBe('unavailable')
})
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd web/frontend && npx vitest run src/services/__tests__/systemSettingsContract.spec.ts`
Expected: FAIL because current `SystemSettingsMeta` does not expose section-level metadata and `buildSystemSettingsSnapshot()` only accepts `datasource`.

- [ ] **Step 3: Write the minimal implementation**

```ts
type SectionScope = 'system' | 'user'
type SectionReadWriteStatus = 'available' | 'unavailable' | 'degraded' | 'local-only'
type SectionEvidenceType = 'measured' | 'inferred' | 'historical-baseline'

type SystemSettingsSnapshotInput = {
  datasource: unknown | null
  notification: unknown | null
}

const SECTION_META = {
  general: { scope: 'system', owner: 'system-settings', readStatus: 'unavailable', writeStatus: 'unavailable', evidenceType: 'inferred' },
  datasource: { scope: 'system', owner: 'data-source-config', readStatus: 'available', writeStatus: 'available', evidenceType: 'measured' },
  notification: { scope: 'user', owner: 'notification-preferences', readStatus: 'available', writeStatus: 'available', evidenceType: 'measured' },
  security: { scope: 'system', owner: 'system-settings', readStatus: 'unavailable', writeStatus: 'unavailable', evidenceType: 'inferred' },
} as const
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd web/frontend && npx vitest run src/services/__tests__/systemSettingsContract.spec.ts`
Expected: PASS with section metadata assertions green.

- [ ] **Step 5: Commit**

```bash
git add web/frontend/src/services/TradingApiManager.types.ts \
        web/frontend/src/services/systemSettingsContract.ts \
        web/frontend/src/services/__tests__/systemSettingsContract.spec.ts
git commit -m "feat[frontend]: add sectioned system-settings metadata"
```

## Task 2: Compose Existing Datasource And Notification Truths

**Files:**
- Modify: `web/frontend/src/services/TradingApiManager.ts`
- Modify: `web/frontend/src/api/user.ts`
- Test: `web/frontend/src/services/__tests__/TradingApiManager.system-settings.spec.ts`

- [ ] **Step 1: Write the failing composition tests**

```ts
it('reads datasource and notification through their canonical owners', async () => {
  getDataSourceConfigMock.mockResolvedValue({ success: true, data: { providers: ['akshare'] } })
  getNotificationSettingsMock.mockResolvedValue({ email_enabled: true })

  const snapshot = await new TradingApiManager().getSystemSettings()

  expect(snapshot.datasource).toEqual({ providers: ['akshare'] })
  expect(snapshot.notification).toEqual({ email_enabled: true })
})

it('routes notification writes through the canonical notification preferences API', async () => {
  updateNotificationSettingsMock.mockResolvedValue(undefined)

  await expect(
    new TradingApiManager().saveSystemSettings({
      notification: { email_enabled: false },
    }),
  ).resolves.toBe(true)

  expect(updateNotificationSettingsMock).toHaveBeenCalledWith({ email_enabled: false })
})
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd web/frontend && npx vitest run src/services/__tests__/TradingApiManager.system-settings.spec.ts`
Expected: FAIL because current manager ignores `notification` on read and rejects `notification` writes.

- [ ] **Step 3: Write the minimal implementation**

```ts
async getSystemSettings(): Promise<SystemSettings> {
  const [datasource, notification] = await Promise.all([
    dataApiCompat.getDatasourceSettings(),
    userApiCompat.getNotificationSettings(),
  ])

  return buildSystemSettingsSnapshot({
    datasource: datasource.data,
    notification: notification.data,
  })
}

async saveSystemSettings(settings: Partial<SystemSettings>): Promise<boolean> {
  assertSupportedSystemSettingsWrite(settings)

  const writes: Promise<unknown>[] = []
  if (settings.datasource) writes.push(dataApiCompat.saveDatasourceSettings(settings.datasource))
  if (settings.notification) writes.push(userApiCompat.saveNotificationSettings(settings.notification))
  await Promise.all(writes)
  return true
}
```

And align:

```ts
async getNotificationSettings(): Promise<NotificationSettings> {
  return request.get(`${this.notificationUrl}/preferences`)
}

async updateNotificationSettings(settings: UpdateNotificationSettingsPayload): Promise<void> {
  await request.post(`${this.notificationUrl}/preferences`, settings)
}
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd web/frontend && npx vitest run src/services/__tests__/TradingApiManager.system-settings.spec.ts src/services/__tests__/systemSettingsContract.spec.ts`
Expected: PASS with datasource and notification composition green.

- [ ] **Step 5: Commit**

```bash
git add web/frontend/src/services/TradingApiManager.ts \
        web/frontend/src/api/user.ts \
        web/frontend/src/services/__tests__/TradingApiManager.system-settings.spec.ts
git commit -m "feat[frontend]: compose sectioned system-settings truths"
```

## Task 3: Surface Section Truth In Store And Page Messaging

**Files:**
- Modify: `web/frontend/src/stores/system.ts`
- Modify: `web/frontend/src/views/system/Settings.vue`
- Test: `web/frontend/tests/unit/views/system-wrapper-retention.spec.ts`
- Test: `web/frontend/tests/unit/config/system-route-canonical-paths.spec.ts`

- [ ] **Step 1: Write the failing UI/state test**

```ts
it('keeps the canonical system settings page path while exposing section-aware messaging', () => {
  expect(systemRoute.component).toContain('/views/system/Settings.vue')
  expect(renderedBannerText).toContain('notification preferences are user-scoped')
})
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd web/frontend && npx vitest run tests/unit/views/system-wrapper-retention.spec.ts tests/unit/config/system-route-canonical-paths.spec.ts`
Expected: FAIL because current page banner only reports a blanket degraded/local-storage message.

- [ ] **Step 3: Write the minimal implementation**

```ts
const sectionSummary = [
  'datasource uses the canonical system data-source config backend',
  'notification uses the canonical user notification preferences backend',
  'general/security remain unavailable until system-scoped contracts land',
]
```

Also remove or quarantine any store-level local persistence that would become a second source of truth for the same sectioned data.

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd web/frontend && npx vitest run tests/unit/views/system-wrapper-retention.spec.ts tests/unit/config/system-route-canonical-paths.spec.ts`
Expected: PASS with canonical route retention intact and section messaging updated.

- [ ] **Step 5: Commit**

```bash
git add web/frontend/src/stores/system.ts \
        web/frontend/src/views/system/Settings.vue \
        web/frontend/tests/unit/views/system-wrapper-retention.spec.ts \
        web/frontend/tests/unit/config/system-route-canonical-paths.spec.ts
git commit -m "feat[frontend]: surface section-aware system settings status"
```

## Task 4: Add Canonical System-Scoped General And Security APIs

**Files:**
- Create: `web/backend/app/api/v1/system/settings.py`
- Modify: `web/backend/app/api/v1/system/__init__.py`
- Modify: `web/backend/app/api/v1/router.py`
- Test: `web/backend/tests/test_system_settings_contract.py`
- Test: `web/backend/tests/test_health_route_conflicts.py`

- [ ] **Step 1: Write the failing backend tests**

```python
def test_system_settings_routes_exist_in_openapi(client):
    schema = client.get('/openapi.json').json()
    assert '/api/v1/system/settings/general' in schema['paths']
    assert '/api/v1/system/settings/security' in schema['paths']

def test_general_settings_read_write_contract(client):
    payload = {'timezone': 'Asia/Shanghai', 'default_backtest_concurrency': 4}
    assert client.post('/api/v1/system/settings/general', json=payload).status_code == 200
    assert client.get('/api/v1/system/settings/general').status_code == 200
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest web/backend/tests/test_system_settings_contract.py web/backend/tests/test_health_route_conflicts.py -q`
Expected: FAIL because the system settings routes are not registered.

- [ ] **Step 3: Write the minimal implementation**

```python
router = APIRouter(prefix="/settings", tags=["System Settings"])

@router.get("/general")
async def get_general_settings():
    return {...}

@router.post("/general")
async def update_general_settings(payload: GeneralSettingsPayload):
    return {...}

@router.get("/security")
async def get_security_settings():
    return {...}

@router.post("/security")
async def update_security_settings(payload: SecuritySettingsPayload):
    return {...}
```

Use one explicit canonical persistence owner for these sections. Do not add `*_new.py`, backup mirrors, or a second config store.

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest web/backend/tests/test_system_settings_contract.py web/backend/tests/test_health_route_conflicts.py -q`
Expected: PASS with new routes visible in OpenAPI and contract behavior green.

- [ ] **Step 5: Commit**

```bash
git add web/backend/app/api/v1/system/settings.py \
        web/backend/app/api/v1/system/__init__.py \
        web/backend/app/api/v1/router.py \
        web/backend/tests/test_system_settings_contract.py \
        web/backend/tests/test_health_route_conflicts.py
git commit -m "feat[backend]: add system-scoped settings contract"
```

## Task 5: Retire Local-Storage Fallback Under Section Exit Gates

**Files:**
- Modify: `web/frontend/src/views/system/Settings.vue`
- Modify: `web/frontend/src/stores/system.ts`
- Test: `web/frontend/src/services/__tests__/TradingApiManager.system-settings.spec.ts`
- Test: `web/frontend/src/services/__tests__/systemSettingsContract.spec.ts`

- [ ] **Step 1: Write the failing retirement test**

```ts
it('does not persist sectioned system settings through localStorage once all sections are canonical', () => {
  expect(window.localStorage.setItem).not.toHaveBeenCalledWith(
    'artdeco-system-settings',
    expect.any(String),
  )
})
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd web/frontend && npx vitest run src/services/__tests__/TradingApiManager.system-settings.spec.ts src/services/__tests__/systemSettingsContract.spec.ts`
Expected: FAIL while local-storage fallback is still active.

- [ ] **Step 3: Write the minimal implementation**

```ts
if (snapshot.meta.sections.general.readStatus === 'available' &&
    snapshot.meta.sections.datasource.readStatus === 'available' &&
    snapshot.meta.sections.notification.readStatus === 'available' &&
    snapshot.meta.sections.security.readStatus === 'available') {
  // remove legacy local-only save path
}
```

Also document code-path judgment and function-tree judgment for every deleted fallback path before removing it.

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd web/frontend && npx vitest run src/services/__tests__/TradingApiManager.system-settings.spec.ts src/services/__tests__/systemSettingsContract.spec.ts`
Expected: PASS with no local-only persistence path remaining for canonical sections.

- [ ] **Step 5: Commit**

```bash
git add web/frontend/src/views/system/Settings.vue \
        web/frontend/src/stores/system.ts \
        web/frontend/src/services/__tests__/TradingApiManager.system-settings.spec.ts \
        web/frontend/src/services/__tests__/systemSettingsContract.spec.ts
git commit -m "refactor[frontend]: retire legacy system-settings local fallback"
```

## Verification Matrix

- Frontend contract tests:
  - `cd web/frontend && npx vitest run src/services/__tests__/systemSettingsContract.spec.ts src/services/__tests__/TradingApiManager.system-settings.spec.ts`
- Frontend route retention tests:
  - `cd web/frontend && npx vitest run tests/unit/views/system-wrapper-retention.spec.ts tests/unit/config/system-route-canonical-paths.spec.ts`
- Frontend quality gates:
  - `cd web/frontend && npx eslint --no-warn-ignored src/services/systemSettingsContract.ts src/services/TradingApiManager.ts src/views/system/Settings.vue src/stores/system.ts src/api/user.ts`
  - `cd web/frontend && npx vue-tsc --noEmit --pretty false`
- Backend contract tests:
  - `pytest web/backend/tests/test_system_settings_contract.py web/backend/tests/test_health_route_conflicts.py -q`
- OpenSpec gate:
  - `openspec validate add-sectioned-system-config-contract --strict`

## Governance Notes

- `notification` stays user-scoped for the whole rollout; do not mirror it into a system-global store.
- Any temporary compatibility layer must be thin, owner-tagged, and scheduled for removal.
- `measured`, `inferred`, and `historical-baseline` labels must remain distinct in code and UI.
- Do not delete fallback or compatibility paths until both code-path and function-tree judgments are recorded.
