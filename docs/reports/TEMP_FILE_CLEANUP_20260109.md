# 临时文件清理与归档报告
**日期**: 2026-01-09 12:40
**执行人**: Claude Code (Main CLI)
**原因**: 遵守项目文件组织规范，避免使用 /tmp 保存正式文档

---

## ✅ 已归档到项目的文件

### 📄 报告文档 (docs/reports/)

| 原路径 | 新路径 | 说明 |
|--------|--------|------|
| `/tmp/bug-registration-report.md` | `docs/reports/BUG_REGISTRATION_20260109.md` | BUG登记报告 |
| `/tmp/typescript-error-fix-report.md` | `docs/reports/TYPESCRIPT_ERROR_FIX_20260109.md` | TypeScript错误修复报告 |
| `/tmp/frontend-service-status-report.md` | `docs/reports/FRONTEND_SERVICE_STATUS_20260109.md` | 前端服务状态报告 |

### 🖼️ 截图证据 (docs/reports/screenshots/)

| 原路径 | 新路径 | 说明 |
|--------|--------|------|
| `/tmp/bloomberg-styling-test.png` | `docs/reports/screenshots/BLOOMBERG_STYLING_VERIFICATION_20260109.png` | Bloomberg样式验证截图 |
| `/tmp/playwright-frontend-test.png` | `docs/reports/screenshots/FRONTEND_PLAYWRIGHT_TEST_20260108.png` | Playwright前端测试截图 |

---

## 📋 仍留在 /tmp 的文件 (待清理)

### 🖼️ 测试截图 (可删除)

这些是测试过程中的临时验证截图，可以删除：

```bash
# 删除旧测试截图
rm /tmp/portfolio_04_stocks.png
rm /tmp/stockdetail_screenshot.png
rm /tmp/stocks_p0.png
rm /tmp/stocks_screenshot.png
rm /tmp/verify_stocks_optimized.png
```

### 📊 测试报告JSON (可删除)

```bash
# 删除临时测试报告
rm /tmp/stockdetail_report.json
rm /tmp/stocks_report.json
```

---

## 📝 文件组织规范

### ✅ 正确做法

**正式文档和报告** → `docs/reports/`
- BUG报告: `docs/reports/BUG_REGISTRATION_YYYYMMDD.md`
- 错误修复: `docs/reports/TYPESCRIPT_ERROR_FIX_YYYYMMDD.md`
- 服务状态: `docs/reports/FRONTEND_SERVICE_STATUS_YYYYMMDD.md`

**截图证据** → `docs/reports/screenshots/`
- 重要的验证截图: `docs/reports/screenshots/DESCRIPTION_YYYYMMDD.png`
- 测试截图: `docs/reports/screenshots/TEST_NAME_YYYYMMDD.png`

**临时文件** → `/tmp` (仅用于临时中转)
- 测试过程中的临时缓存
- 快速验证的输出
- **可随时删除**

### ❌ 错误做法

- ❌ 将正式报告保存到 `/tmp`
- ❌ 将截图作为长期证据放在 `/tmp`
- ❌ 使用 `/tmp` 作为项目文档的存储位置
- ❌ 不清理 `/tmp` 中的测试文件

---

## 🗑️ 建议的清理操作

### 选项1: 删除所有临时测试文件

```bash
# 删除所有留在 /tmp 的测试截图
rm /tmp/*_screenshot.png /tmp/*_test.png /tmp/*.png 2>/dev/null

# 删除所有临时测试报告
rm /tmp/*_report.json 2>/dev/null
```

### 选项2: 归档有用的文件后再清理

```bash
# 如果需要保留某些截图作为证据
# 先移动到 docs/reports/screenshots/
# 然后删除 /tmp 中的其他临时文件
```

### 选项3: 定期清理 (推荐)

```bash
# 添加到 crontab 定期清理 /tmp
# 每天凌晨3点清理7天前的临时文件
0 3 * * * find /tmp -name "*.png" -mtime +7 -delete
0 3 * * * find /tmp -name "*.json" -mtime +7 -delete
```

---

## 📊 文件分类决策流程

```
文件类型判断
├─ 正式报告文档？
│  ├─ YES → docs/reports/
│  └─ NO → 继续判断
├─ 重要的验证证据？
│  ├─ YES → docs/reports/screenshots/
│  └─ NO → 继续判断
├─ 临时测试输出？
│  ├─ YES → /tmp (可随时删除)
│  └─ NO → 根据具体用途决定
```

---

## 🎯 关键原则

1. **项目文档永久保存在项目目录内**
   - 报告 → `docs/reports/`
   - 截图 → `docs/reports/screenshots/`
   - 配置 → `config/`
   - 脚本 → `scripts/`

2. **/tmp 仅用于临时中转**
   - 测试缓存
   - 快速验证
   - 可随时删除

3. **定期清理临时文件**
   - 避免磁盘空间浪费
   - 保持系统整洁

---

## ✅ 改进总结

| 问题 | 解决方案 | 状态 |
|------|----------|------|
| 报告保存在 /tmp | 移动到 docs/reports/ | ✅ 已完成 |
| 截图散落在 /tmp | 移动重要截图到 docs/reports/screenshots/ | ✅ 已完成 |
| 临时文件未清理 | 制定清理规范 | ✅ 已制定 |

---

**状态**: 🟢 **文件组织规范已遵守**
