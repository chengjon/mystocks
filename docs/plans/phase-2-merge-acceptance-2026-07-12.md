# Phase 2 合并交付验收报告

> **日期**: 2026-07-12
> **阶段**: Phase 2 — 同主题扩展文档合并（P0 + P1 迁移项 #1-#7）
> **状态**: 全部完成，待用户验收

---

## 一、任务总览

| 编号 | 迁移项 | 源文件数 | 合并目标 | 状态 |
|------|--------|----------|----------|------|
| P0-1 | Apifox 指南 | 4 | `docs/api/apifox-guide.md` | ✅ |
| P0-2 | 错误码/异常处理 | 3 | `docs/api/error-codes.md` | ✅ |
| P0-3 | API 契约管理/测试 | 2 | `docs/api/contracts/README.md` + 全文归档 | ✅ |
| P1-5 | 部署指南 | 3 | `docs/ops/deployment.md` | ✅ |
| P1-6 | 监控指南 | 3 合并 + 3 保留 | `docs/ops/monitoring.md` | ✅ |
| P1-7 | 排障指南 | 2 | `docs/ops/troubleshooting.md` | ✅ |
| — | INDEX 重写 | 1 | `docs/INDEX.md`（轻量导航） | ✅ |

**源文件合计**: 20 份 → **合并手册 6 份** + **重定向头 19 处** + **归档 4 份**（其中 3 份归档兼有重定向头）

---

## 二、新增合并手册（6 份）

| 文件 | 行数 | 合并来源 | 关键处理 |
|------|------|----------|----------|
| `docs/api/apifox-guide.md` | 264 | BEGINNER + IMPORT + QUICK_START (去重合并) | 逻辑重组：5 分钟上手 → 导入方法 → 认证 → 示例 → 同步 → 高级 → 排查 |
| `docs/api/error-codes.md` | 286 | ERROR_CODES + ERROR_CODE_GUIDE + EXCEPTION_HANDLER_GUIDE | 错误码参考表 (1xxx-9xxx) + 全局异常处理器 + 最佳实践 |
| `docs/api/contracts/README.md` | 141 | CONTRACT_MANAGEMENT_API + CONTRACT_TESTING_API | 总览/索引层（规范层/管理层/测试层）；源码级全文归档至 archive/ |
| `docs/ops/deployment.md` | 214 | DEPLOYMENT + PORT_CONFIGURATION + deployment-guide | **端口修正**: 3000-3009/8000-8009 → 实际 3020/8020（备用 3021/8021，QM 3030/8030） |
| `docs/ops/monitoring.md` | 274 | MONITORING_GUIDE + OPTIMIZATION_DEPLOYMENT + 告警规则 + INDEX | 核心结构来自 GUIDE；验证命令来自 OPTIMIZATION；告警规则+坑点来自告警规则文档；3 个子系统保留原位链接 |
| `docs/ops/troubleshooting.md` | 448 | TROUBLESHOOTING + TROUBLESHOOTING_QUICK_REFERENCE | Q&A 结构 + 诊断 bash 脚本 + CI/CD 章节 + 快速修复命令表 + 报告模板 |

---

## 三、重定向头清单（19 处）

合并后，源文件顶部添加统一格式重定向头，格式：
```
> ⚠️ 已合并（2026-07-12）
> 本文档已合并至 [目标路径]。
> 本文件仅作历史参考，不再维护。
```

### 3.1 Apifox 组（3 份）
| 源文件 | 行数 | 行为 |
|--------|------|------|
| `docs/api/APIFOX_BEGINNER_GUIDE.md` | 670 → 675 | 重定向至 apifox-guide.md |
| `docs/api/APIFOX_IMPORT_GUIDE.md` | 575 → 580 | 重定向至 apifox-guide.md |
| `docs/api/APIFOX_QUICK_START.md` | 361 → 366 | 重定向至 apifox-guide.md |

### 3.2 错误码/异常组（3 份）
| 源文件 | 行数 | 行为 |
|--------|------|------|
| `docs/api/ERROR_CODES.md` | 184 → 189 | 重定向至 error-codes.md |
| `docs/api/ERROR_CODE_GUIDE.md` | 401 → 406 | 重定向至 error-codes.md |
| `docs/api/EXCEPTION_HANDLER_GUIDE.md` | 479 → 484 | 重定向至 error-codes.md |

### 3.3 API 契约组（4 份 — 2 份全文归档 + 2 份极简重定向）
| 源文件 | 行数 | 行为 |
|--------|------|------|
| `docs/api/CONTRACT_MANAGEMENT_API.md` | → 5 | 全文归档至 archive/，原位留 5 行重定向 |
| `docs/api/CONTRACT_TESTING_API.md` | → 5 | 全文归档至 archive/，原位留 5 行重定向 |
| `docs/api/APIFOX_IMPORT_SUCCESS.md` | → 5 | 一次性完成报告，归档至 archive/ |
| `docs/api/apifox_mcp_playwright使用.md` | → 5 | 已废弃文档，归档至 archive/ |

### 3.4 部署组（3 份）
| 源文件 | 行数 | 行为 |
|--------|------|------|
| `docs/operations/deployment/DEPLOYMENT.md` | 442 → 447 | 重定向至 ops/deployment.md |
| `docs/operations/deployment/PORT_CONFIGURATION.md` | 227 → 232 | 重定向至 ops/deployment.md |
| `docs/operations/deployment-guide.md` | 44 → 49 | 重定向至 ops/deployment.md |

### 3.5 监控组（4 份 — 3 合并 + 1 INDEX 更新）
| 源文件 | 行数 | 行为 |
|--------|------|------|
| `docs/operations/monitoring/MONITORING_GUIDE.md` | 222 → 227 | 重定向至 ops/monitoring.md |
| `docs/operations/monitoring/MYSTOCKS_MONITORING_OPTIMIZATION_DEPLOYMENT.md` | 283 → 288 | 重定向至 ops/monitoring.md（部署步骤+验证命令章节） |
| `docs/operations/monitoring/告警规则设置方法.md` | 282 → 287 | 重定向至 ops/monitoring.md（告警规则+坑点章节） |
| `docs/operations/monitoring/INDEX.md` | 27 → 28 | 更新：标注合并后保留的子系统文档 |

### 3.6 排障组（2 份）
| 源文件 | 行数 | 行为 |
|--------|------|------|
| `docs/operations/TROUBLESHOOTING.md` | 384 → 390 | 重定向至 ops/troubleshooting.md |
| `docs/operations/TROUBLESHOOTING_QUICK_REFERENCE.md` | 580 → 586 | 重定向至 ops/troubleshooting.md |

---

## 四、归档文件（4 份 → docs/archive/api-standalone-docs/）

| 文件 | 行数 | 归类原因 |
|------|------|----------|
| `apifox-import-success-2025-11-10.md` | 224 | 一次性完成报告（2025-11-10），已过时效 |
| `apifox-mcp-playwright-legacy.md` | 120 | 已废弃的使用方式 |
| `contract-management-api-full.md` | 1005 | 源码级全文（过长不适为手册参考），总览已提取到 contracts/README.md |
| `contract-testing-api-full.md` | 729 | 源码级全文（过长不适为手册参考），总览已提取到 contracts/README.md |

**archive/ 目录结构**:
```
docs/archive/
└── api-standalone-docs/
    ├── apifox-import-success-2025-11-10.md
    ├── apifox-mcp-playwright-legacy.md
    ├── contract-management-api-full.md
    └── contract-testing-api-full.md
```

---

## 五、保留未动的子系统文档（monitoring/ 内 3 份）

以下文档内容专精、受众不同，原位保留并在 ops/monitoring.md 中以"子系统文档"链接：

| 文件 | 行数 | 说明 |
|------|------|------|
| `docs/operations/monitoring/ASYNC_MONITORING_GUIDE.md` | 459 | 异步监控系统使用指南（事件驱动架构） |
| `docs/operations/monitoring/SIGNAL_MONITORING_METRICS_DESIGN.md` | 900 | 交易信号 Prometheus 指标设计（9 个指标） |
| `docs/operations/monitoring/TMUX_LNAV_ADAPTER_MONITORING.md` | 315 | tmux + lnav 适配器日志监控方案 |

---

## 六、Phase 1 同步交付物（与 Phase 2 同期完成）

| 文件 | 行数 | 用途 |
|------|------|------|
| `docs/CORE.md` | 77 | 全文档体系主入口 |
| `docs/INDEX.md` | 40 | 轻量导航（指向 CORE.md） |
| `docs/dev/index.md` | 55 | 开发手册主页 |
| `docs/test/index.md` | 88 | 测试手册主页 |
| `docs/ai/index.md` | 62 | AI 协作手册主页 |

---

## 七、关键决策记录

### 7.1 端口配置修正
- **问题**: 部署文档端口描述 (3000-3009/8000-8009) 与实际 (.env: FRONTEND_PORT=3020, BACKEND_PORT=8020) 不符
- **决策**: 合并手册统一使用实际端口 3020/8020，标注备用端口 3021/8021，新增 QM 专用 3030/8030

### 7.2 监控文档拆解策略
- **问题**: 7 份监控文档覆盖 4 个不同受众（全栈运维 / 交易系统 / 适配器调试 / 异步架构）
- **决策**: 核心 3 份合并为 ops/monitoring.md（日常运维入口）；3 个专精子系统保留原位（链接引用）

### 7.3 契约文档分层
- **问题**: CONTRACT 两份源码级文档合计 2,700+ 行，作为日常手册过长
- **决策**: 提取总览层 (141 行 README) 入手册；全文归档至 archive/ 备查

### 7.4 废弃文档识别
- **问题**: APIFOX_IMPORT_SUCCESS（完成报告）与 apifox_mcp_playwright（废弃用法）不适合合并
- **决策**: 整体归档至 archive/api-standalone-docs/，原位留 5 行重定向

---

## 八、源文件→合并目标 映射表（验收核对用）

```
[P0-1 Apifox] → docs/api/apifox-guide.md (264 行)
  ├─ docs/api/APIFOX_BEGINNER_GUIDE.md ─────────────┐
  ├─ docs/api/APIFOX_IMPORT_GUIDE.md ───────────────┤ 去重 + 逻辑重组
  ├─ docs/api/APIFOX_QUICK_START.md ────────────────┘
  └─ docs/api/APIFOX_IMPORT_SUCCESS.md → archive/ (一次性完成报告)

[P0-2 错误码] → docs/api/error-codes.md (286 行)
  ├─ docs/api/ERROR_CODES.md ───────────────────────┐
  ├─ docs/api/ERROR_CODE_GUIDE.md ──────────────────┤ 去重合并
  └─ docs/api/EXCEPTION_HANDLER_GUIDE.md ───────────┘

[P0-3 契约] → docs/api/contracts/README.md (141 行) + archive/ 全文
  ├─ docs/api/CONTRACT_MANAGEMENT_API.md ───────────→ 5 行重定向 + archive/ (1005 行)
  └─ docs/api/CONTRACT_TESTING_API.md ──────────────→ 5 行重定向 + archive/ (729 行)

[P1-5 部署] → docs/ops/deployment.md (214 行)
  ├─ docs/operations/deployment/DEPLOYMENT.md ──────┐
  ├─ docs/operations/deployment/PORT_CONFIGURATION.md┤ 端口修正 + 去重
  └─ docs/operations/deployment-guide.md ───────────┘

[P1-6 监控] → docs/ops/monitoring.md (274 行) + 3 个子系统保留
  ├─ docs/operations/monitoring/MONITORING_GUIDE.md ────────────┐
  ├─ docs/operations/monitoring/MYSTOCKS_MONITORING_OPTIMIZATION_DEPLOYMENT.md ┤ 合并
  ├─ docs/operations/monitoring/告警规则设置方法.md ────────────┘
  ├─ docs/operations/monitoring/ASYNC_MONITORING_GUIDE.md ──────→ 保留原位
  ├─ docs/operations/monitoring/SIGNAL_MONITORING_METRICS_DESIGN.md → 保留原位
  └─ docs/operations/monitoring/TMUX_LNAV_ADAPTER_MONITORING.md → 保留原位

[P1-7 排障] → docs/ops/troubleshooting.md (448 行)
  ├─ docs/operations/TROUBLESHOOTING.md ────────────┐
  └─ docs/operations/TROUBLESHOOTING_QUICK_REFERENCE.md ┤ 合并
```

---

## 九、验收核对项

- [ ] 6 份合并手册内容完整（覆盖源文件核心内容）
- [ ] 19 处重定向头格式统一、链接有效（含 3 份归档兼有重定向）
- [ ] 4 份归档文件完整可查
- [ ] 端口配置 (3020/8020) 在 deployment.md 中正确呈现
- [ ] 监控子系统链接在 monitoring.md 中有效
- [ ] contracts/README.md 归档引用路径正确
- [ ] INDEX.md → CORE.md 入口链路有效
- [ ] dev/test/ai index.md 手册主页正常

---

## 十、下一步待 Phase 3

Phase 3 涉及高量级操作（约 1,246 份 reports/ 一次性报告归档），需用户**明确确认**后执行：
- 归档 reports/ 下阶段报告/修复报告/分析报告
- 归档独立 API 文档
- 清理冗余链接

**Phase 2 验收通过后，再启动 Phase 3。**
