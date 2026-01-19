# MyStocks E2E测试 - 快速参考指南

## 🚀 快速开始

### 重新运行测试
```bash
cd /opt/claude/mystocks_spec/web/frontend
node e2e-test-runner.mjs
```

### 查看结果
```bash
# 查看JSON报告
cat test-reports/e2e-report.json | jq '.summary'

# 查看最新截图
ls -lht test-reports/e2e-screenshots/ | head -5

# 查看执行日志
tail -100 ../../test-reports/e2e-execution.log
```

---

## 📊 测试结果摘要

| 指标 | 结果 | 状态 |
|------|------|------|
| **总测试数** | 13 | - |
| **通过** | 1 (7.7%) | 🔴 |
| **失败** | 12 (92.3%) | 🔴 |
| **后端API** | 1/5 (20%) | 🔴 |
| **前端页面** | 0/8 (0%) | 🔴 |

---

## 🔴 关键问题

### 1. apiClient.ts模块加载失败 (P0)
```bash
# 诊断命令
curl -I http://localhost:3002/src/api/apiClient.ts
pm2 logs mystocks-frontend --err --lines 50

# 预期: HTTP 200
# 实际: HTTP 500
```

### 2. 所有页面空白 (P0)
```
症状: HTTP 200但内容为空
原因: apiClient.ts加载失败导致Vue应用崩溃
影响: 所有功能不可用
```

### 3. 后端API 404错误 (P1)
```bash
# 检查后端路由
curl http://localhost:8000/docs
grep -r "api/v1/market" web/backend/app/
```

---

## 📁 文件位置

### 测试脚本
- **E2E测试脚本**: `web/frontend/e2e-test-runner.mjs`
- **任务计划**: `task_plan.md`
- **发现笔记**: `notes.md`

### 测试报告
- **详细报告**: `test-reports/E2E_TEST_FINAL_REPORT.md`
- **JSON报告**: `web/frontend/test-reports/e2e-report.json`
- **执行日志**: `test-reports/e2e-execution.log`

### 证据附件
- **截图目录**: `web/frontend/test-reports/e2e-screenshots/`
- **控制台日志**: `web/frontend/test-reports/e2e-logs/`

---

## 🔧 修复检查清单

### Step 1: 修复apiClient.ts加载失败
- [ ] 检查TypeScript编译错误
  ```bash
  cd web/frontend
  npx tsc --noEmit src/api/apiClient.ts
  ```
- [ ] 查看Vite开发服务器错误日志
  ```bash
  pm2 logs mystocks-frontend --err --lines 100
  ```
- [ ] 验证模块导入路径
- [ ] 重启前端服务
  ```bash
  pm2 restart mystocks-frontend
  ```

### Step 2: 修复后端API路由
- [ ] 检查FastAPI路由注册
  ```bash
  cd web/backend
  grep -r "api/v1/market" app/
  ```
- [ ] 验证路由版本号
- [ ] 确认API前缀配置
- [ ] 重启后端服务
  ```bash
  pm2 restart mystocks-backend
  ```

### Step 3: 验证修复
- [ ] 重新运行E2E测试
  ```bash
  cd web/frontend
  node e2e-test-runner.mjs
  ```
- [ ] 检查测试通过率提升
- [ ] 验证页面内容非空
- [ ] 验证DOM元素可见

---

## ✅ 成功标准

修复后的目标：
- ✅ 前端页面通过率 > 80%
- ✅ 后端API通过率 = 100%
- ✅ 无控制台JS错误
- ✅ 所有页面核心元素可见
- ✅ 页面标题符合预期

---

## 📞 下一步行动

### 立即 (今天)
1. 修复apiClient.ts加载失败
2. 修复后端API路由
3. 验证修复结果

### 短期 (本周)
1. 补充测试覆盖剩余页面
2. 添加前后端联动测试
3. 添加交互测试

### 长期 (本月)
1. 集成到CI/CD
2. 添加性能测试
3. 添加可访问性测试

---

## 🎓 测试方法论

本次测试遵循的核心原则：

1. **✅ 不仅检查HTTP 200**
   - 所有页面返回200但仍判定失败
   - 验证了HTML内容、DOM渲染、元素可见性

2. **✅ 优先使用toBeVisible()**
   - 确保元素不仅在DOM中，还完成CSS渲染
   - 避免了"DOM存在但页面空白"的误判

3. **✅ 必须捕获控制台错误**
   - 成功捕获apiClient.ts加载失败
   - 直接定位了问题根本原因

4. **✅ 前后端解耦验证**
   - 先测后端API（1/5通过）
   - 再测前端页面（0/8通过）
   - 明确区分前后端问题

5. **✅ 截图/录屏追溯**
   - 8张失败截图
   - 证明系统性问题

6. **✅ 明确问题分类**
   - 🔴 前端加载问题
   - 🔴 前端渲染问题
   - 🟠 后端接口问题
   - 🟡 前端显示问题

---

**最后更新**: 2026-01-18 23:04:11
**测试工程师**: Claude Code
**测试工具**: Playwright + Chrome DevTools MCP
