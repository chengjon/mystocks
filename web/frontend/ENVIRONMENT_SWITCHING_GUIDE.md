# 前端环境切换指南

## 📋 概述

项目支持两种运行模式：
- **Mock模式**: 使用Mock数据，无需后端数据库（开发/测试推荐）
- **Real模式**: 使用真实后端API，连接实际数据库（生产环境）

## 🔄 快速切换

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

编辑 `.env` 文件，设置 `VITE_APP_MODE`：

```bash
# Mock模式
VITE_APP_MODE=mock

# Real模式
VITE_APP_MODE=real
```

## 🔍 验证当前模式

### 查看浏览器控制台

前端启动时会输出当前使用的API端点：

```
[Strategy API] Using Mock endpoint: /api/mock/strategy
# 或
[Strategy API] Using Real endpoint: /api/v1/strategy
```

### 检查网络请求

打开浏览器开发者工具 → Network标签：
- Mock模式: 请求 `/api/mock/strategy/strategies`
- Real模式: 请求 `/api/v1/strategy/strategies`

## ⚙️ 配置对比

| 配置项 | Mock模式 | Real模式 |
|--------|----------|----------|
| `VITE_APP_MODE` | `mock` | `real` |
| API端点 | `/api/mock/strategy` | `/api/v1/strategy` |
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
1. 检查前端 `.env` 文件的 `VITE_APP_MODE`
2. 检查后端 `.env` 文件的 `USE_MOCK_DATA`
3. 重启前后端服务

### 问题2: Real模式下API返回404

**原因**: 后端服务未启动或USE_MOCK_DATA=false导致API未注册

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

- [Mock/Real数据切换指南](../../guides/MOCK_REAL_DATA_SWITCHING_GUIDE.md) - 后端数据源切换
- [Mock数据使用规则](../../guides/MOCK_DATA_USAGE_RULES.md) - Mock数据规范
- [API验证报告](../../reports/api_verification/) - API可用性验证

---

**最后更新**: 2026-01-02
**维护者**: Main CLI (Claude Code)
