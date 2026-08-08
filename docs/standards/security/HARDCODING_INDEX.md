# 硬编码规范索引

> 项目:`mystocks_spec` · 生成日期:2026-08-08
> 范围:所有硬编码(hardcoding)治理相关的规则、指南、扫描脚本、CI 接入点、豁免清单。

## 一、规则与配置层(权威源)

| 全路径 | 作用 |
|---|---|
| `/opt/claude/mystocks_spec/config/security/hardcoding-rules.yml` | **规则定义**(7 条 P0-P2 正则规则、扫描范围、扩展名白名单) |
| `/opt/claude/mystocks_spec/config/security/hardcoding_exceptions.yml` | **豁免清单**(白名单条目,记录豁免理由、责任人、到期日) |

## 二、规范与指南层(文档)

| 全路径 | 作用 |
|---|---|
| `/opt/claude/mystocks_spec/docs/standards/security/HARDCODING_GOVERNANCE_TIERING_GUIDE.md` | **核心分级指南**(P0-P4 五级模型、治理动作、CI 门禁基线、Vault 集成示例) |
| `/opt/claude/mystocks_spec/docs/standards/security/SECURITY_BEST_PRACTICES.md` | 安全最佳实践(覆盖硬编码防护) |
| `/opt/claude/mystocks_spec/docs/standards/security/SECURITY_CODING_STANDARDS.md` | 安全编码规范 |
| `/opt/claude/mystocks_spec/docs/standards/security/SECURITY_CI_CD_INTEGRATION.md` | CI/CD 安全集成(detect-secrets/gitleaks/trufflehog/bandit 工具链) |
| `/opt/claude/mystocks_spec/docs/standards/security/SECURITY_TESTING_GUIDELINES.md` | 安全测试指南 |
| `/opt/claude/mystocks_spec/docs/standards/SECURITY_QUICK_REFERENCE.md` | 安全速查 |
| `/opt/claude/mystocks_spec/docs/standards/SECURITY_REMEDIATION_GUIDE.md` | 安全整改指南 |
| `/opt/claude/mystocks_spec/docs/standards/PHASE0_CREDENTIAL_ROTATION_GUIDE.md` | 凭据轮换 SOP(硬编码泄露应急) |
| `/opt/claude/mystocks_spec/architecture/STANDARDS.md` | 工程红线("二、技术工程红线"章节涉及硬编码禁令) |

## 三、扫描脚本层(强制工具链)

| 全路径 | 作用 |
|---|---|
| `/opt/claude/mystocks_spec/scripts/security/hardcoding_scan.py` | **主扫描器**(按 `hardcoding-rules.yml` 扫描运行时代码) |
| `/opt/claude/mystocks_spec/scripts/security/validate_hardcoding_exceptions.py` | **豁免校验器**(校验 `hardcoding_exceptions.yml` 字段完整性、到期日) |
| `/opt/claude/mystocks_spec/scripts/security/basic_security_check.py` | 基础安全检查,包含 `check_hardcoded_secrets` |
| `/opt/claude/mystocks_spec/scripts/dev/check_hardcoded_secrets.py` | dev 入口(开发者本地快速扫描) |
| `/opt/claude/mystocks_spec/scripts/dev/debt_analyzer/performance_security_analyzer.py` | 技术债分析器,内含 `_check_hardcoded_secrets`(由 `process_security_for_file` 调用) |
| `/opt/claude/mystocks_spec/scripts/ai_enhancer/analyzer.py` | AI 增强分析器,定义 `hardcoded_patterns` 模式集 |

## 四、CI/CD 门禁接入

| 全路径 | 作用 |
|---|---|
| `/opt/claude/mystocks_spec/.github/workflows/security-enhancement.yml` | 安全增强工作流(执行硬编码扫描) |
| `/opt/claude/mystocks_spec/.github/workflows/code-quality.yml` | 代码质量门禁(集成硬编码检测) |

## 五、测试覆盖

| 全路径 | 作用 |
|---|---|
| `/opt/claude/mystocks_spec/tests/test_security_xss_csrf.py` | 包含 `test_no_hardcoded_secrets`(回归测试,防止新增硬编码) |

## 六、相关历史报告(参考,非现行规范)

| 全路径 | 作用 |
|---|---|
| `/opt/claude/mystocks_spec/docs/reports/SECURITY_HARDcoded_PASSWORD_SCAN_REPORT.md` | 历史硬编码密码扫描报告 |
| `/opt/claude/mystocks_spec/docs/standards/SECURITY_AUDIT_REPORT_20251130.md` | 2025-11-30 安全审计 |
| `/opt/claude/mystocks_spec/docs/standards/SECURITY_AUDIT_REPORT_2025-12-23.md` | 2025-12-23 安全审计 |
| `/opt/claude/mystocks_spec/docs/standards/SECURITY_FOLLOWUP_PLAN_20251130.md` | 跟进计划 |
| `/opt/claude/mystocks_spec/docs/reports/SECURITY_FIX_*.md` | 历次修复实施记录 |

## 七、Worktree 副本(只读镜像,非权威)

`/opt/claude/mystocks_spec/.claude/worktrees/b4-014-milestone/` 下有同名副本,**不得作为权威源**。所有规则修改必须改 `config/security/` 下的根目录文件。

## 八、快速判定流程

1. **新增代码** → 对照 `HARDCODING_GOVERNANCE_TIERING_GUIDE.md` 第 10 节快速判定表
2. **本地扫描** → `python scripts/dev/check_hardcoded_secrets.py`
3. **CI 强制门禁** → `security-enhancement.yml` 触发 `hardcoding_scan.py`
4. **正当例外** → 在 `hardcoding_exceptions.yml` 登记字段(`id`/`level`/`reason`/`owner`/`due_date`)
5. **P0 泄露应急** → 走 `PHASE0_CREDENTIAL_ROTATION_GUIDE.md`

## 九、规则分级速记

| 级别 | 数量 | 阻断 | 典型场景 |
|---|---|---|---|
| P0 | 3 条 | 是 | 明文凭据、连接串带账号、已知默认密钥 |
| P1 | 2 条 | 是(IP/默认值) | 硬编码 IPv4、`os.getenv` 带静态默认值 |
| P2 | 3 条 | 否(告警) | localhost HTTP/WS、127.0.0.1 URL |
