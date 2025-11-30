# 端口分配指南 (Port Allocation Guide)

**项目**: MyStocks Spec
**强制执行**: 🔒 MANDATORY
**生效日期**: 2025-11-30

---

## 快速参考 (Quick Reference)

```
┌──────────────────────────────────────────┐
│     MyStocks Spec 端口范围分配           │
├──────────────────────────────────────────┤
│                                          │
│  🔵 前端 (Frontend):   3000-3009        │
│  🔴 后端 (Backend):    8000-8009        │
│                                          │
└──────────────────────────────────────────┘
```

### 启动命令速查

```bash
# ✅ 检查端口分配状态
bash scripts/dev/check-port-allocation.sh

# ✅ 启动前端 (Vite on 3000)
cd web/frontend && npm run dev -- --port 3000

# ✅ 启动后端 (FastAPI on 8000)
python -m uvicorn web.backend.app.main:app --port 8000

# ✅ 运行 E2E 测试
npx playwright test
```

---

## 前端端口范围 (Frontend: 3000-3009)

### 主要用途

| 端口 | 用途 | 优先级 |
|------|------|--------|
| 3000 | 主开发服务器 | 首选 |
| 3001-3009 | 备用/多开发实例 | 按需 |

### 启动方式

```bash
# 方式 1: 使用 npm run dev (指定端口)
cd web/frontend
npm run dev -- --port 3000

# 方式 2: 使用环境变量
VITE_PORT=3002 npm run dev

# 方式 3: 修改 vite.config.js
// vite.config.js
export default {
  server: {
    port: 3000
  }
}
```

### 验证

```bash
# 检查端口是否可用
lsof -i :3000 && echo "❌ Occupied" || echo "✅ Available"

# 检查 Vite 是否启动成功
curl http://localhost:3000 | head -20
```

---

## 后端端口范围 (Backend: 8000-8009)

### 主要用途

| 端口 | 用途 | 优先级 |
|------|------|--------|
| 8000 | FastAPI 主服务 | 首选 |
| 8001-8009 | 备用/微服务 | 按需 |

### 启动方式

```bash
# 方式 1: 使用 uvicorn (指定端口)
python -m uvicorn web.backend.app.main:app --port 8000

# 方式 2: 使用环境变量
BACKEND_PORT=8001 python -m uvicorn web.backend.app.main:app

# 方式 3: 修改启动脚本
# 编辑 .env 文件
BACKEND_PORT=8000
```

### 验证

```bash
# 检查端口是否可用
lsof -i :8000 && echo "❌ Occupied" || echo "✅ Available"

# 检查 FastAPI 是否启动成功
curl http://localhost:8000/api/health
```

---

## 端口冲突排查 (Troubleshooting)

### 问题 1: 端口已被占用 (Port Already in Use)

```bash
# 找出占用端口的进程
lsof -i :3000

# 输出示例:
# COMMAND   PID   USER   FD   TYPE DEVICE SIZE/OFF NODE NAME
# node    12345   user   20u  IPv4 xxxxx      0t0  TCP *:3000 (LISTEN)

# 方案 A: 杀死进程
kill -9 12345

# 方案 B: 使用不同的端口
npm run dev -- --port 3001
# 更新 playwright.config.js 中的 baseURL
```

### 问题 2: E2E 测试连接失败 (E2E Test Connection Failed)

```bash
# 检查：
# 1. 前端是否启动（3000-3009）
lsof -i :3000

# 2. 后端是否启动（8000-8009）
lsof -i :8000

# 3. playwright.config.js 配置是否正确
grep "baseURL" web/frontend/playwright.config.js

# 修正：
# 确保 baseURL 指向正确的前端端口
# 示例: baseURL: 'http://localhost:3000'
```

### 问题 3: 多个 Vite 实例冲突 (Multiple Vite Instances)

```bash
# 关闭所有 npm/node 进程
pkill -f "npm run dev"

# 检查是否都关闭了
ps aux | grep -E "npm|node|vite" | grep -v grep

# 重新启动 (指定端口)
npm run dev -- --port 3000
```

---

## 监督和执行 (Enforcement)

### 自动化检查

E2E 测试运行前，系统会自动验证端口配置：

```javascript
// 测试启动前检查
beforeAll(async () => {
  const baseURL = process.env.BASE_URL || 'http://localhost:3000';
  const port = new URL(baseURL).port;

  if (!['3000','3001',...'3009'].includes(port)) {
    throw new Error(`❌ Invalid port: ${port}. Use 3000-3009`);
  }
});
```

### 手动检查

```bash
# 运行端口分配检查脚本
bash scripts/dev/check-port-allocation.sh

# 输出示例:
# ✅ Port 3000: Available
# ❌ Port 3001: Occupied by node (PID: 12345)
# ✅ Available ports: 3002 3003 3004 ...
```

### 违规处理 (Violation Handling)

| 级别 | 描述 | 处理 |
|------|------|------|
| 🟡 Level 1 | 代码审查中发现端口配置错误 | 要求修正 |
| 🟠 Level 2 | PR 中多次出现违规 | 阻止合并 |
| 🔴 Level 3 | 频繁违规 | 团队会议讨论 |

---

## 常见场景 (Common Scenarios)

### 场景 1: 全新开发环境启动

```bash
# 步骤 1: 检查端口
bash scripts/dev/check-port-allocation.sh

# 步骤 2: 启动后端 (Terminal 1)
python -m uvicorn web.backend.app.main:app --port 8000

# 步骤 3: 启动前端 (Terminal 2)
cd web/frontend && npm run dev -- --port 3000

# 步骤 4: 运行 E2E 测试 (Terminal 3)
npx playwright test
```

### 场景 2: 端口 3000 被占用

```bash
# 步骤 1: 查看占用情况
lsof -i :3000
# 假设输出: node (PID: 12345)

# 步骤 2: 选择替代方案
# 方案 A: 杀死旧进程
kill -9 12345

# 方案 B: 使用新端口
npm run dev -- --port 3001

# 步骤 3: 更新测试配置 (如果使用非 3000 端口)
# 编辑 web/frontend/playwright.config.js
# baseURL: 'http://localhost:3001'
```

### 场景 3: 多个开发者同时工作

```bash
# 开发者 1
npm run dev -- --port 3000
python -m uvicorn ... --port 8000

# 开发者 2 (同一台机器)
npm run dev -- --port 3002
python -m uvicorn ... --port 8001

# 确保各自的 .env 和配置文件指向正确的端口
# 开发者 2 的 playwright.config.js:
# baseURL: 'http://localhost:3002'
```

---

## 配置文件检查清单 (Configuration Checklist)

```bash
# ✅ .env 文件
VITE_PORT=3000
VITE_API_BASE=http://localhost:8000

# ✅ web/frontend/playwright.config.js
baseURL: 'http://localhost:3000'

# ✅ web/frontend/vite.config.js
server: {
  port: 3000
}

# ✅ 后端启动命令
--port 8000
```

---

## 快速命令参考 (Command Cheatsheet)

```bash
# 📊 检查状态
bash scripts/dev/check-port-allocation.sh

# 🔵 前端
cd web/frontend && npm run dev -- --port 3000
VITE_PORT=3001 npm run dev

# 🔴 后端
python -m uvicorn web.backend.app.main:app --port 8000
python -m uvicorn web.backend.app.main:app --port 8001

# 🧪 测试
npx playwright test
BASE_URL=http://localhost:3001 npx playwright test

# 🔍 排查
lsof -i :3000          # 查看占用端口 3000 的进程
kill -9 <PID>          # 杀死进程
pkill -f "npm run dev" # 杀死所有 npm 进程
```

---

## 常见问题 (FAQ)

**Q: 为什么要限制在 3000-3009 和 8000-8009？**
A: 这些范围避免了系统保留端口和其他服务的冲突，同时为多个开发实例预留了足够的端口。

**Q: 能否使用其他端口？**
A: 不能。端口范围是硬性要求。如果需要特殊情况，请与团队讨论。

**Q: 如何在多个项目间切换端口？**
A: 为每个项目使用不同的端口（3001, 3002 等）和不同的 .env 文件。

**Q: E2E 测试失败怎么办？**
A: 首先运行 `bash scripts/dev/check-port-allocation.sh` 验证端口配置。

---

## 支持和帮助 (Support)

遇到端口相关问题？

1. **快速诊断**: `bash scripts/dev/check-port-allocation.sh`
2. **查看本指南**: 这个文档
3. **查看 CLAUDE.md**: 详细的端口规范要求
4. **联系团队**: 如有特殊需求，请与开发负责人联系

---

**最后更新**: 2025-11-30
**文档版本**: 1.0
**强制级别**: 🔒 MANDATORY
