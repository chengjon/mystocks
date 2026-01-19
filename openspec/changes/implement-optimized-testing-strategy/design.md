# Technical Design: Implement Optimized Testing Strategy

## Context

MyStocks项目当前面临严重的测试基础设施问题：
- ESM模块导入错误导致Vue应用无法渲染
- 前端服务器稳定性差，频繁启停
- 测试工具链分散，缺乏协同机制
- 缺乏系统化的测试分层策略

基于实际测试经验和Web测试方法论，需要建立完整的测试体系来解决这些问题。

## Goals / Non-Goals

### Goals
- 建立稳定的ESM兼容性测试环境
- 实现PM2统一的服务管理和健康检查
- 创建分层测试执行框架（环境→后端→前端→全栈→性能）
- 整合多工具协同工作机制
- 实现AI助手深度集成测试优化

### Non-Goals
- 重写现有测试用例（仅优化执行环境和策略）
- 修改核心业务逻辑
- 替换现有测试框架
- 改变项目架构

## Decisions

### 1. ESM兼容性处理策略

**决策**: 使用Vite别名配置强制ESM版本 + 预构建排除

**备选方案考虑**:
- 方案A: 替换为date-fns库
  - 优点: 完全兼容，功能丰富
  - 缺点: 需要重构所有日期处理代码，工作量大
- 方案B: 保持dayjs但配置ESM别名
  - 优点: 保持现有API，最小化代码变更
  - 缺点: 可能仍有边缘情况兼容性问题

**选择理由**: 方案B工作量小，风险可控，且通过实际测试验证有效

### 2. 服务稳定性保障方案

**决策**: PM2生态系统管理 + 健康检查机制

**架构设计**:
```javascript
// PM2配置文件结构
{
  apps: [{
    name: 'mystocks-frontend',
    script: 'npm run dev',
    health_check: { url: 'http://localhost:3001', timeout: 5000 },
    dependencies: ['mystocks-backend'] // 服务依赖关系
  }, {
    name: 'mystocks-backend',
    script: 'python -m uvicorn app.main:app',
    args: ['--host', '0.0.0.0', '--port', '8000'],
    interpreter: 'python'
  }]
}
```

**优势**: 自动重启、健康监控、日志聚合、服务依赖管理

### 3. 分层测试执行框架

**决策**: Phase 0-6的渐进式测试策略

**执行顺序**:
```
Phase 0: ESM兼容性预处理
Phase 1: PM2环境固化
Phase 2: Pytest后端测试
Phase 3: Schemathesis API契约测试
Phase 4: Vitest前端组件测试
Phase 5: Playwright全栈E2E测试
Phase 6: Locust性能压力测试
```

**设计原则**: 每个Phase都有明确的验证标准，失败时可准确定位问题

### 4. 多工具协同机制

**决策**: 基于PM2的统一入口 + 脚本自动化

**协同架构**:
```bash
# 统一测试执行脚本
test-runner.sh:
├── environment_check()  # PM2服务验证
├── backend_test()       # Pytest执行
├── api_contract_test()  # Schemathesis验证
├── frontend_test()      # Vitest + Playwright
└── performance_test()   # Locust压力测试
```

## Risks / Trade-offs

### 技术风险
- **ESM兼容性边缘情况**: 某些第三方库可能仍有兼容性问题
  - 缓解: 建立监控机制，及时发现并处理
- **PM2配置复杂性**: 多服务依赖关系可能导致启动顺序问题
  - 缓解: 实施健康检查和重试机制

### 性能风险
- **测试执行时间延长**: 分层测试可能增加总执行时间
  - 缓解: 并行执行可并行化的测试阶段
- **资源消耗增加**: 多工具同时运行可能消耗更多系统资源
  - 缓解: 实施资源监控和限制机制

### 维护风险
- **配置同步问题**: 多工具配置可能出现不一致
  - 缓解: 建立配置验证和自动化同步机制
- **依赖版本冲突**: 测试工具间可能存在版本兼容性问题
  - 缓解: 定期进行依赖审计和兼容性测试

## Migration Plan

### 部署步骤
1. **Phase 1**: ESM兼容性配置
   - 更新Vite配置添加dayjs别名
   - 验证Vue应用正常渲染

2. **Phase 2**: PM2环境管理
   - 创建PM2生态配置文件
   - 部署启动验证脚本
   - 培训团队使用PM2管理服务

3. **Phase 3**: 测试框架集成
   - 配置各测试工具的协同脚本
   - 建立测试执行流水线
   - 实施监控和报告机制

### 回滚策略
- **ESM配置回滚**: 移除Vite别名配置，恢复原dayjs导入方式
- **PM2回滚**: 停止PM2管理，恢复手动服务启动方式
- **测试框架回滚**: 保留原有测试脚本，可随时切换

### 验证标准
- ✅ ESM导入错误: 0个
- ✅ Vue应用渲染: 正常
- ✅ 服务器稳定性: PM2进程正常运行
- ✅ 测试执行: 分层策略正常工作
- ✅ 工具协同: 无冲突，正常集成