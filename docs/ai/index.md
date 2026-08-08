# AI 工具手册

> **版本**: 1.0 | **更新日期**: 2026-07-12
> **维护者**: AI 工具链
> **文档类型**: 手册主页
> **上游入口**: [CORE.md](../CORE.md) → AI 工具角色

---

## 本手册范围

覆盖 LLM API 调用、AI 工具链、prompt 工程、量化 AI 策略。

---

## 快速入口

| 场景 | 文档 | 简介 |
|------|------|------|
| LLM API 文档 | [ai/LLMS_API_DOCUMENTATION.md](../api/LLMS_API_DOCUMENTATION.md) | LLM 接口清单、请求/响应示例 |
| AI 工具链 | [ai-prompts/( ai-prompts/)] | prompt 模板、AI 使用指南 |
| 量化 AI 策略 | [guides/quant-trading/](../guides/quant-trading/) | 量化策略回测 |
| GPU 加速 | [gpu_api_system/](../gpu_api_system/) | 可选 GPU 加速 |
| AI 协作配置 | [scripts/ai-collaboration-setup.sh](../../scripts/ai-collaboration-setup.sh) | AI 协作初始化 |
| AI 测试优化 | `.github/workflows/ai-test-optimization.yml` | GitHub Actions workflow |
| AI 验证扩展 | [api/CI_CD_Validation_Extension_Guide.md](../api/CI_CD_Validation_Extension_Guide.md) | 5. AI 增强验证扩展章节 |

---

## AI 工具使用流程

1. **读取官方 doc**：通过 `context7` MCP 获取最新库文档（优先于 web search）
2. **配置 LLM API**：按 `LLMS_API_DOCUMENTATION.md` 配置密钥和端点
3. **加载 prompt 模板**：从 `ai/prompts/` 加载领域 prompt
4. **本地验证**：通过 workflow 中 AI 验证扩展校验结果
5. **CI 上报**：`ai-test-optimization.yml` 自动记录 token 消耗与命中率

---

## 与 CI/CD 联动

| 工作流 | 用途 |
|--------|------|
| `ai-test-optimization.yml` | AI 测试用例生成优化 |
| `quantum-strategy-validation.yml` | 量子/量化策略验证 |
| `quant-strategy-validation.yml` | 量化策略验证 |

---

## 相关工具

| 工具 | 用途 |
|------|------|
| Claude Code | AI 编码助手（MCP + skills） |
| SearXNG | web_search MCP 后端 |
| Codex MCP | 非交互式 AI 编码 |
| GitNexus MCP | RAG 代码知识图谱 |
| Context7 MCP | 库文档查阅 |

---

> 跨手册链接：开发入口 [dev/](../dev/index.md) · 测试入口 [test/](../test/index.md)
