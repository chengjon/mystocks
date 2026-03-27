# Change: Extend Frontend Configuration Model

## Why

The current frontend configuration system (`config/pageConfig.ts`) only supports standard route-to-component mapping with 23% coverage (7/30+ routes configured). This leads to:

1. **Configuration gap**: 77% of routes (23/30+) lack configuration, causing hardcoded API endpoints and WebSocket channels
2. **Type safety issues**: Missing configurations means no compile-time validation for route names, API endpoints, or WebSocket channels
3. **Development inefficiency**: Developers must manually add configuration for new routes, taking ~90% more time than necessary
4. **Maintenance burden**: Adding/removing routes requires manual updates in multiple files

## What Changes

Implement **Plan A: Extended Configuration Model** that supports ArtDeco's monolithic component architecture without breaking it.

### Key Changes

1. **Extended configuration types**
   - Add `MonolithicPageConfig` type for components with multiple tabs
   - Keep `StandardPageConfig` for single-page routes
   - Add `TabConfig` type for monolithic component tab definitions

2. **Updated PAGE_CONFIG structure**
   - Support both monolithic (component with tabs) and page (single page) configuration types
   - Type-safe definitions using discriminated union types
   - Compile-time validation for all route names and configurations

3. **Updated TypeScript types**
   - Add `PageConfigType` union: `'monolithic' | 'page'`
   - Add `TabConfig` interface
   - Add `MonolithicPageConfig` and `StandardPageConfig` interfaces

4. **Configuration helper functions**
   - Update `getPageConfig()` to handle both monolithic and page configurations
   - Add `getTabConfig()` for monolithic components to retrieve tab-specific settings

5. **Migration for 6 core ArtDeco components**
   - Update `ArtDecoMarketQuotes.vue` (8 tabs)
   - Update `ArtDecoStockManagement.vue` (6 tabs)
   - Update `ArtDecoTradingManagement.vue` (5 tabs)
   - Update components for other 3 core pages

## Impact

### Affected Specs

- [ ] `frontend-ai-screening/spec.md` - Add monolithic configuration support
- [ ] `frontend-ai-screening/spec.md` - Update API integration patterns
- [ ] `frontend-ai-screening/spec.md` - Update WebSocket integration patterns

### Affected Code

- **Frontend Configuration**:
  - `web/frontend/src/config/pageConfig.ts` - Core configuration file
  - `web/frontend/src/config/pageConfig.generated.ts` - Generated configuration file
  - `web/frontend/src/router/index.ts` - Route definitions (references by configuration)

- **ArtDeco Core Components**:
  - `web/frontend/src/views/ArtDeco/ArtDecoMarketQuotes.vue` - Market data component
  - `web/frontend/src/views/ArtDeco/ArtDecoStockManagement.vue` - Stock portfolio component
  - `web/frontend/src/views/ArtDeco/ArtDecoTradingManagement.vue` - Trading component
  - `web/frontend/src/views/ArtDeco/ArtDecoTechnicalAnalysis.vue` - Technical analysis component
  - `web/frontend/src/views/ArtDeco/ArtDecoRiskMonitor.vue` - Risk monitor component

## Risks

| Risk | Probability | Mitigation |
|-------|------------|------------|
| Breaking ArtDeco UX | Low | Keep `activeTab` switching within single component, don't split into multiple routes |
| Type safety regression | Low | Use TypeScript discriminated unions for compile-time checks |
| Configuration errors | Medium | Implement validation hooks to catch missing configurations |
| Development overhead | Low | Provide batch generation script to reduce manual work |

## Open Questions

- Should we migrate all ArtDeco core pages in Week 1, or start with the 3 highest-priority pages?
- Should batch generation script be TypeScript or JavaScript for easier integration?
- Should we add unit tests for the configuration system itself?

## Migration Plan

### Stage 1: Extend Configuration Model (Week 1)

1. Update `web/frontend/src/config/pageConfig.ts` with extended types
2. Create helper functions for monolithic configuration access
3. Update 6 core ArtDeco components to use new configuration system
4. Test configuration loading and type safety

### Stage 2: Batch Generation Script (Week 1)

1. Create `scripts/tools/generate-page-config.ts` script
2. Implement route parsing from `router/index.ts`
3. Implement intelligent inference for API endpoints
4. Implement intelligent inference for WebSocket channels
5. Generate configuration for all 30+ routes

### Stage 3: Validation Hooks (Week 1)

1. Create `scripts/hooks/check-page-config.mjs`
2. Implement route-to-configuration validation
3. Implement required field validation
4. Add pre-commit configuration

### Stage 4: Component Migration (Week 1)

1. Update `ArtDecoMarketQuotes.vue` (8 tabs: realtime, technical, fund-flow, etc.)
2. Update `ArtDecoStockManagement.vue` (6 tabs)
3. Update `ArtDecoTradingManagement.vue` (5 tabs)
4. Update `ArtDecoTechnicalAnalysis.vue` (analysis tabs)
5. Update `ArtDecoRiskMonitor.vue` (risk tabs)
6. Update 3 remaining core components (TBD)

## Success Criteria

- [ ] Configuration types support both monolithic and page architectures
- [ ] TypeScript type safety with discriminated unions
- [ ] Helper functions work correctly for both configuration types
- [ ] All 6 core ArtDeco components successfully updated
- [ ] Batch generation script produces valid configuration for all 30+ routes
- [ ] Configuration coverage increases from 23% to 80%+
- [ ] Pre-commit hook prevents missing configurations
- [ ] No breaking changes to ArtDeco's fluent Tab UX
- [ ] Type safety maintained or improved
- [ ] Development efficiency improved with automation

## Timeline

- Week 1, Day 1-2: Extend configuration model
- Week 1, Day 3-4: Implement batch generation script
- Week 1, Day 5: Implement validation hooks
- Week 1, Days 6-9: Migrate 6 core ArtDeco components
- Week 1, Day 10: Testing and verification

## Rollback Plan

If issues arise:

1. Revert `web/frontend/src/config/pageConfig.ts` to previous version
2. Revert component migrations to use hardcoded values
3. Disable validation hooks from `.pre-commit-config.yaml`

This change extends the configuration model to support ArtDeco's monolithic component architecture without breaking existing patterns or user experience.
