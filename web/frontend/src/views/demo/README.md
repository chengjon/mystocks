# Demo Pages Directory

> **参考指南说明**:
> 本文件用于提供 Web 子系统的使用方法、操作指引、接口接入说明、排障提示或结构参考，帮助理解局部实现与协作方式。
> 其中的步骤、示例、端口、目录和操作建议应先与 `architecture/STANDARDS.md`、当前代码实现及最新验证结果核对；若涉及仓库执行流程、命令或协作约束，再补充参考根目录 `AGENTS.md`。本文件不得单独视为仓库共享规则或当前状态的唯一事实来源。


This directory contains demonstration, experimental, and research pages that are not part of the main production application.

## Pages in This Directory

### 1. FreqtradeDemo.vue
- **Purpose**: Demonstration of Freqtrade integration
- **Status**: Demo/Research
- **Size**: ~808 lines
- **API Integration**: Minimal
- **Note**: Reference implementation for Freqtrade bot integration

### 2. OpenStockDemo.vue
- **Purpose**: OpenStock API demonstration
- **Status**: Demo/Research
- **Size**: ~1362 lines (Large component)
- **API Integration**: Multiple API calls
- **Note**: Comprehensive demo of stock data APIs

### 3. StockAnalysisDemo.vue
- **Purpose**: Stock analysis demonstration
- **Status**: Demo/Research
- **Size**: ~1090 lines (Large component)
- **API Integration**: Multiple endpoints
- **Note**: Research implementation for advanced stock analysis

### 4. TdxpyDemo.vue
- **Purpose**: TDXpy library integration demo
- **Status**: Demo/Research
- **Size**: ~873 lines
- **API Integration**: Direct API calls
- **Note**: Reference for TDX market data integration

### 5. PyprofilingDemo.vue
- **Purpose**: Python profiling tool demonstration
- **Status**: Demo/Research
- **Size**: ~805 lines
- **API Integration**: Limited
- **Note**: Research implementation for performance profiling

### 6. Phase4Dashboard.vue
- **Purpose**: Phase 4 development dashboard (legacy)
- **Status**: Legacy Demo
- **Size**: ~592 lines
- **API Integration**: Partial
- **Note**: Historical development milestone

### 7. Wencai.vue
- **Purpose**: Wencai API integration demo
- **Status**: Demo/Research
- **Size**: ~289 lines
- **API Integration**: Basic
- **Note**: Reference for Wencai data source

## Important Notes

These pages are **NOT** part of the main production application and should:

1. **Not be deployed** to production environment
2. **Not be tested** in standard E2E test suites
3. **Be referenced** only for research/development purposes
4. **Be refactored** before use in production

## Development & Testing

If you need to work with demo pages:

1. Use the demo path: `/demo/FreqtradeDemo` (if routing enables it)
2. Test independently from production pages
3. Follow the same code quality standards as production
4. Document any dependencies clearly

## Migration Path

When converting a demo page to production:

1. Extract core functionality into separate components
2. Standardize API integration (use `@/api` pattern)
3. Add comprehensive error handling
4. Add loading state management
5. Add user feedback mechanisms (ElMessage)
6. Move to appropriate production directory
7. Add E2E tests following P1 page patterns

## Quality Standards

Demo pages do not need to meet production quality standards but should:
- ✅ Have clear documentation
- ✅ Include basic error handling
- ✅ Use modern Vue 3 syntax
- ⚠️ May have large components (refactoring recommended)
- ⚠️ May have inconsistent patterns
- ⚠️ May not have full test coverage

---

**Last Updated**: 2025-11-27
**Organization**: Phase 9 - Infrastructure Optimization
