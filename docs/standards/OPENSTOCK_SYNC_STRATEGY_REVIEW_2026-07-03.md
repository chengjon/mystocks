# OpenStock 同步策略审核 — 方案 A 否决理由修正 + 遗漏方案补充

**审核人**: Claude (deepseek-v4-pro)
**审核日期**: 2026-07-03
**审核对象**: `docs/standards/OPENSTOCK_SYNC_STRATEGY.md` (未 commit)
**触发**: 用户质疑方案 A 否决理由 + 提出两个替代方案

---

## 一、方案 A 否决理由修正

### 原文

> **陷阱 1（决定性）— Host 不一致 + 网络拓扑**：
> GitHub CI 拉 submodule 时走公网，公网无法访问内网 Gitea。
> **结论**：否决。Host 拓扑决定性否决。

### 问题

「决定性否决」太绝对。实测验证：

```
本机 → GitHub: ✅ git ls-remote git@github.com:chengjon/mystocks.git  → 6a85851
本机 → Gitea:   ✅ git ls-remote http://192.168.123.104:3001/john/openstock.git → f99c332
```

**本地开发场景下，方案 A 完全可用**。阻塞点仅在于 GitHub Actions 的托管 runner（公网）无法访问内网 Gitea。且有三种变通：

| 变通 | 做法 |
|------|------|
| CI skip submodule | clone 不加 `--recursive`，CI 用方案 C drift check 替代 |
| Self-hosted runner | 在 NAS 部署 GitHub Actions runner（runner 在内网可访问 Gitea） |
| submodule URL `insteadOf` | 本地用内网 URL，CI 用 GitHub 镜像 URL（需 openstock 也推 GitHub） |

### 建议修正

将「Host 拓扑决定性否决」改为：

> 方案 A 在**本地开发**完全可用（本机 WSL 同时可达 GitHub 和 Gitea）。
> 阻塞点仅在 **GitHub Actions CI**（公网 runner 无法访问内网 Gitea，mystocks 有 39 个 workflow）。
> 变通方案存在（CI skip submodule / self-hosted runner），但综合考虑「CI 改造」+「submodule 整仓源码耦合（陷阱 3）」→ 不推荐作为首选项。

---

## 二、遗漏方案 F — 三仓统一迁入 Gitea NAS

### 方案描述

mystocks / openstock / quantix-rust 全部 host 在同一 Gitea 实例（`192.168.123.104:3001`）。

### 分析

| 维度 | 评价 |
|------|------|
| submodule 可行性 | ✅ 三仓同 host，纯内网直连，无跨 host 问题 |
| CI | ⚠️ 需迁移 39 个 GitHub Actions workflow → Gitea Actions 或本地 cron/runner |
| 社区可见性 | ❌ 丢失 GitHub star / issue / PR 生态 |
| 迁移成本 | 高（三仓全迁 + CI 全重写） |

### 结论

该方案从 Host 拓扑角度是 submodule 路线的正确落点，但 **39 个 CI workflow 的迁移成本过高**。不应作为推荐方案，但应在文档中列入作为完整参考。

---

## 三、新增方案 G — openstock 迁 GitHub 私有仓 + submodule（推荐）

### 方案描述

将 openstock 从 Gitea NAS 推送至 GitHub 私有仓（`chengjon/openstock`），然后在 mystocks 中以 submodule 引用。

```
┌──────────────────────────────────┐
│  GitHub                          │
│                                  │
│  chengjon/mystocks    (public)   │
│  chengjon/openstock   (private)  │  ← 从 Gitea 迁入
│  chengjon/quantix-rust (public?) │
│                                  │
│  submodule 互拉 → 全部同 host    │
│  GitHub Actions → CI 原生可用    │
└──────────────────────────────────┘
```

### 为什么这是最优解

| 对比维度 | 方案 G | 原方案 A（Gitea submodule） | 方案 C（drift check） | 方案 F（全迁 Gitea） |
|----------|--------|---------------------------|---------------------|---------------------|
| 本地开发 | ✅ | ✅ | ✅ | ✅ |
| CI 可用 | ✅ **原生兼容** | ❌ 需变通 | ❌ 脚本手动 | ⚠️ 需全迁 39 workflows |
| 改动范围 | **仅 openstock 一仓** | mystocks 加 submodule | 零迁仓 | 三仓全迁 |
| openstock 大小 | 24 MB / 177 文件 | 同 | 同 | 同 |
| drift 风险 | **零**（commit 级 pin） | 零 | ⚠️ 最长 30 天窗口 | 零 |
| 敏感文件 | 0 个 .env / secret | 同 | 同 | 同 |

### CI 集成：一行配置

GitHub Actions 访问私有 submodule 是标准模式：

```yaml
- uses: actions/checkout@v4
  with:
    submodules: recursive
    token: ${{ secrets.SUBMODULE_PAT }}   # ← 只需这一行
```

PAT 配置：
- 类型：GitHub fine-grained personal access token
- 权限：`repo` scope（仅读私有仓，不需要 workflow / admin）
- 有效期：最长 1 年（到期前 renew）
- 注入位置：mystocks repo → Settings → Secrets → `SUBMODULE_PAT`

### 本地开发

你已经在用 SSH 拉 GitHub——同一个 key 即可拉私有 submodule：

```bash
git clone --recursive git@github.com:chengjon/mystocks.git
# openstock submodule 自动拉取，无需额外配置
```

### 与方案 D（发布制）的关系

不互斥，而是互补：

- **短期**（本周）：openstock → GitHub 私有 + submodule → 零 drift
- **中期**（1-3 月）：评估是否还需要方案 D 发布制
- **长期**（3-6 月）：openstock 落地 `/sources/categories` endpoint → mystocks 切 runtime 动态拉取 → submodule 降级为纯参考

方案 G 不影响 design.md §2 的长期路线。

### openstock Gitea 原仓处理

| 选项 | 做法 |
|------|------|
| **退役** | GitHub 成为唯一 origin，删除 Gitea 仓 |
| **保留为镜像** | Gitea 设 GitHub 为 upstream mirror，定期同步 |

### 唯一注意事项

| 注意点 | 说明 |
|--------|------|
| PAT 权限最小化 | 仅 `repo` scope，不授予 workflow / admin / org |
| PAT 过期 | 到期前 renew，过期后 CI submodule checkout 会失败（CI log 显式报错，不会静默降级） |
| 私有 → 公开 | 未来若想公开 openstock，GitHub Settings 改 visibility 即可，URL 不变，submodule 不受影响 |

---

## 四、文档修订清单

| # | 严重 | 位置 | 修改 |
|---|------|------|------|
| 1 | 🔴 | §2 方案 A | 修正否决理由：「Host 拓扑决定性否决」→「本地可用，仅 GitHub Actions CI 受限；综合考虑 CI 改造 + 整仓耦合 → 不推荐」 |
| 2 | 🔴 | §2 新增 | 方案 G — openstock 迁 GitHub 私有 + submodule（推荐短期，替代原方案 C） |
| 3 | 🟡 | §2 新增 | 方案 F — 三仓统一迁 Gitea NAS（完整参考，不推荐） |
| 4 | 🟡 | §1.3 表 | 「Gitea HTTP 可达性 | ✅ 200」加标注 `(从 WSL/NAS 本机)` |
| 5 | 🟡 | §3 短期步骤 | 原「方案 C」替换为「方案 G」作为短期首选，方案 C 降级为备选 |
| 6 | 🟡 | §3 中期评估 | 方案 D 评估时机：因为方案 G 已消除 drift，方案 D 的必要性降低，观察期可延长至 3 个月 |

---

## 五、修订后的推荐路径

### 短期（本周）— 方案 G

| 步骤 | 工件 |
|------|------|
| 1. openstock 推 GitHub 私有仓 | `git remote add github git@github.com:chengjon/openstock.git && git push github main` |
| 2. mystocks 加 submodule | `git submodule add git@github.com:chengjon/openstock.git deps/openstock` |
| 3. 配置 CI PAT | GitHub repo secrets → `SUBMODULE_PAT` |
| 4. 更新 `actions/checkout` | 所有 workflow 加 `submodules: recursive` + `token` |
| 5. 替换 hardcoded frozenset | `OPENSTOCK_STATIC_CATEGORIES` 改为从 `deps/openstock/docs/DATA_CAPABILITY_SCOPE.md` 启动期解析 |

### 中期（1-3 月）

方案 D 评估（drift 已被方案 G 消除，必要性降低；评估重点转向「跨语言消费者的契约包」价值）。

### 长期（3-6 月）

openstock 落地 `/sources/categories` endpoint → mystocks lifespan 动态拉取 → submodule 降级为参考。

---

## 六、与原始 Q1-Q4 的关系

| 问题 | 原推荐 | 修订后 |
|------|--------|--------|
| Q1 — 短期采纳 C？ | 是 | **方案 G 替代 C 成为首选**；C 保留为备选（不愿迁 openstock 到 GitHub 时） |
| Q2 — 开方案 D 提案？ | 先观察 1 月 | 延至 3 个月（方案 G 已消除 drift，方案 D 的紧迫性下降） |
| Q3 — drift check 频率？ | 月 cron | 方案 G 下不再需要 drift check（submodule pin 替代了 drift 检测） |
| Q4 — 文档位置？ | 保留 docs/standards/ | 不变 |
