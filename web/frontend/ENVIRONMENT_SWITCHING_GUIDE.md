# 前端环境切换指南

> **参考指南说明**:
> 本文件用于提供 Web 子系统的使用方法、操作指引、接口接入说明、排障提示或结构参考，帮助理解局部实现与协作方式。
> 其中的步骤、示例、端口、目录和操作建议应先与 `architecture/STANDARDS.md`、当前代码实现及最新验证结果核对；若涉及仓库执行流程、命令或协作约束，再补充参考根目录 `AGENTS.md`。本文件不得单独视为仓库共享规则或当前状态的唯一事实来源。


## 概述

当前前端只有一个生效中的 mock/real 切换真相源：

- `VITE_USE_MOCK_DATA=true`: 显式 mock 模式
- `VITE_USE_MOCK_DATA=false`: 真实后端模式

`VITE_APP_MODE` 仍可能出现在历史文档或旧报告中，但不应再作为当前运行时切换依据。

## 快速切换

### 方法1: 通过环境文件（推荐）

```bash
# 切换到Mock模式
cd /opt/claude/mystocks_spec/web/frontend
cp .env.mock .env

# 切换到Real模式
cd /opt/claude/mystocks_spec/web/frontend
cp .env.real .env
```

### 方法2: 手动配置

编辑 `.env` 文件，设置 `VITE_USE_MOCK_DATA`：

```bash
# Mock模式
VITE_USE_MOCK_DATA=true

# Real模式
VITE_USE_MOCK_DATA=false
```

## 验证当前模式

### 查看浏览器控制台

优先检查前端环境变量和实际请求路径：

- 显式 mock 模式：`VITE_USE_MOCK_DATA=true`
- 真实联调模式：`VITE_USE_MOCK_DATA=false`

### 检查网络请求

打开浏览器开发者工具 → Network 标签：

- 显式 mock 模式：前端经共享 `apiClient` 短路到 `mockApiClient`
- 真实联调模式：请求真实 `/api/v1/...`、`/api/v2/...`、`/health/...` 等后端路径

## ⚙️ 配置对比

| 配置项 | Mock模式 | Real模式 |
|--------|----------|----------|
| `VITE_USE_MOCK_DATA` | `true` | `false` |
| 前端路由方式 | 共享 `apiClient` → `mockApiClient` | 共享 `apiClient` → 真实 `/api` |
| 数据来源 | Mock数据（内存） | PostgreSQL/TDengine |
| 后端依赖 | 无需后端 | 需要后端服务 |

## 🎯 使用场景

### Mock模式适合：
- ✅ 前端开发和调试
- ✅ UI/UX设计和测试
- ✅ 演示和培训
- ✅ CI/CD自动化测试

### Real模式适合：
- ✅ 生产环境部署
- ✅ 端到端功能测试
- ✅ 性能测试和优化
- ✅ 数据分析和验证

## 🔧 后端环境变量

后端通过 `USE_MOCK_DATA` 环境变量控制Mock API注册：

```bash
# .env 文件（项目根目录）

# Mock模式 - 注册Mock API路由
USE_MOCK_DATA=true

# Real模式 - 仅注册真实API路由
USE_MOCK_DATA=false
```

重启后端服务以应用配置：

```bash
pm2 restart mystocks-backend
```

## 📊 完整的环境切换流程

### 从Mock切换到Real：

1. **前端配置**:
   ```bash
   cd /opt/claude/mystocks_spec/web/frontend
   cp .env.real .env
   ```

2. **后端配置**:
   ```bash
   # 确保项目根目录的.env文件中
   USE_MOCK_DATA=false
   ```

3. **重启服务**:
   ```bash
   # 重启后端
   pm2 restart mystocks-backend

   # 重启前端
   npm run dev
   ```

4. **验证切换**:
   - 检查浏览器控制台日志
   - 查看网络请求URL
   - 测试策略管理功能

## 🚨 故障排除

### 问题1: Mock API仍然可用

**原因**: 前端仍使用Mock配置，或后端USE_MOCK_DATA=true

**解决**:
1. 检查前端 `.env` 文件的 `VITE_USE_MOCK_DATA`
2. 检查后端 `.env` 文件的 `USE_MOCK_DATA`
3. 重启前后端服务

### 问题2: Real模式下API返回404

**原因**: 后端服务未启动、真实接口不可达，或你把 mock 验收误当成真实联调

**解决**:
1. 检查后端服务状态: `pm2 status`
2. 查看后端日志: `pm2 logs mystocks-backend`
3. 确认数据库连接正常

### 问题3: 前端控制台无日志输出

**原因**: 浏览器缓存或Vite配置问题

**解决**:
1. 清除浏览器缓存: Ctrl+Shift+R
2. 强制刷新页面: Ctrl+F5
3. 重启前端开发服务器

## 📚 相关文档

- [Mock/Real数据切换指南](../../guides/mock-data/MOCK_REAL_DATA_SWITCHING_GUIDE.md) - 后端数据源切换
- [Mock数据使用规则](../../guides/mock-data/MOCK_DATA_USAGE_RULES.md) - Mock数据规范
- [API验证报告](../../reports/api_verification/) - API可用性验证

---

## 历史口径说明

以下说法视为历史口径，不再代表当前主线：

- `VITE_APP_MODE=mock|real` 是前端唯一切换方式
- `/api/mock/strategy` 是当前策略前端的主动主链入口
- 真实接口失败后静默使用 mock 也可以视为成功

**最后更新**: 2026-04-25
**维护者**: Main CLI (Claude Code)
