# Claude Code Plugin Marketplace 连接问题修复指南

> **创建日期**: 2025-12-23
> **问题**: Failed to clone marketplace repository - GitHub 连接失败

---

## 问题诊断

### 错误信息
```
Warning: Failed to load marketplace 'claude-code-marketplace':
Failed to clone marketplace repository:
Cloning into '/root/.claude/plugins/marketplaces/temp_1766461152583'...
```

### 根本原因
- ❌ 系统无法连接到 `github.com:443`
- ❌ Git 克隆操作超时
- ❌ 网络防火墙或缺少代理配置

---

## 解决方案

### 方案 1: 配置 Git 使用代理 (推荐)

如果你在使用代理服务器（特别是在中国大陆）：

#### 设置 Git 代理

```bash
# HTTP/HTTPS 代理
git config --global http.proxy http://proxy.example.com:8080
git config --global https.proxy http://proxy.example.com:8080

# 或使用 SOCKS5 代理
git config --global http.proxy socks5://127.0.0.1:1080
git config --global https.proxy socks5://127.0.0.1:1080
```

#### 测试连接

```bash
# 测试 Git 连接
git ls-remote https://github.com/anthropics/claude-code.git

# 测试 HTTPS 连接
curl -I https://github.com
```

#### 取消代理（如果不需要）

```bash
git config --global --unset http.proxy
git config --global --unset https.proxy
```

---

### 方案 2: 使用 GitHub 镜像站

#### 修改 Git 配置使用镜像

```bash
# 使用 GitHub 镜像加速（如 ghproxy）
git config --global url."https://ghproxy.com/https://github.com/".insteadOf "https://github.com/"
```

**你的系统当前已配置**:
```bash
url.https://ghp_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX@github.com/.insteadof=https://github.com/
```

⚠️ **注意**: 这个配置使用了 GitHub Token，但 Token 可能已过期或无效。

---

### 方案 3: 使用 SSH 方式克隆 (如果 HTTPS 失败)

#### 1. 生成 SSH 密钥

```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
```

#### 2. 添加到 GitHub

```bash
# 复制公钥
cat ~/.ssh/id_ed25519.pub

# 在 GitHub 设置中添加 SSH 密钥
# Settings -> SSH and GPG keys -> New SSH key
```

#### 3. 测试 SSH 连接

```bash
ssh -T git@github.com
```

#### 4. 配置 Claude Code 使用 SSH

编辑 `/root/.claude/plugins/known_marketplaces.json`，将 HTTPS URL 替换为 SSH URL：

**之前 (HTTPS)**:
```json
{
  "claude-code-marketplace": {
    "source": {
      "source": "git",
      "url": "https://github.com/ananddtyagi/claude-code-marketplace.git"
    }
  }
}
```

**之后 (SSH)**:
```json
{
  "claude-code-marketplace": {
    "source": {
      "source": "git",
      "url": "git@github.com:ananddtyagi/claude-code-marketplace.git"
    }
  }
}
```

---

### 方案 4: 手动克隆 marketplace (绕过 Claude Code)

#### 1. 手动克隆仓库

```bash
cd /root/.claude/plugins/marketplaces
git clone https://github.com/ananddtyagi/claude-code-marketplace.git claude-code-marketplace-manual
```

#### 2. 更新配置文件

编辑 `/root/.claude/plugins/known_marketplaces.json`：

```json
{
  "claude-code-marketplace": {
    "source": {
      "source": "local",
      "path": "/root/.claude/plugins/marketplaces/claude-code-marketplace-manual"
    },
    "installLocation": "/root/.claude/plugins/marketplaces/claude-code-marketplace",
    "lastUpdated": "2025-12-23T12:00:00.000Z"
  }
}
```

---

### 方案 5: 使用已安装的 marketplace (最简单)

**好消息**: 你已经安装了 9 个 marketplaces！

```bash
# 查看已安装的 marketplaces
ls /root/.claude/plugins/marketplaces/
```

**已安装的 marketplace**:
- ✅ `claude-code-plugins` - 官方插件
- ✅ `superpowers-marketplace` - Superpowers 技能
- ✅ `claudeforge-marketplace` - ClaudeForge 插件
- ✅ `anthropic-agent-skills` - 官方技能
- ✅ `claude-code-cookbook` - 食谱插件
- ✅ 其他 4 个

**建议**: 直接使用已安装的 marketplace，暂时忽略更新警告。

---

## 临时解决方案：禁用问题 marketplace

如果你暂时不需要 `claude-code-marketplace`，可以禁用它：

```bash
# 编辑已安装插件列表
vi /root/.claude/plugins/installed_plugins.json

# 找到并移除或注释掉 claude-code-marketplace 相关条目
```

---

## 验证修复

### 测试 1: 检查网络连接

```bash
# 测试 GitHub 连接
curl -I https://github.com

# 预期输出: HTTP/1.1 200 OK
```

### 测试 2: 测试 Git 克隆

```bash
# 克隆测试仓库
cd /tmp
git clone https://github.com/cli/cli.git test-repo

# 如果成功，删除测试仓库
rm -rf test-repo
```

### 测试 3: 测试 Claude Code 插件

```bash
# 重新启动 Claude Code
# 尝试使用 /plugin 命令
```

---

## 推荐方案（根据网络环境）

### 如果你在中国大陆

1. **配置代理** (方案 1) - 最稳定
2. **使用镜像站** (方案 2) - 最快速
3. **手动克隆** (方案 4) - 最可靠

### 如果你不在受限网络环境

1. **检查防火墙** - 允许 GitHub 访问
2. **检查 DNS** - 尝试使用 8.8.8.8 或 1.1.1.1
3. **联系网络管理员** - 确认 GitHub 访问策略

### 如果你有 SSH 访问权限

1. **使用 SSH 克隆** (方案 3) - 最安全
2. **配置 SSH 密钥** - 避免密码输入

---

## 当前系统配置摘要

### Git 配置
- Git 版本: 2.43.0 ✅
- GitHub Token URL 重写: 已配置 ⚠️ (可能失效)
- 代理: 未配置 ❌

### 网络状态
- GitHub HTTPS 连接: 失败 ❌
- 超时时间: 133 秒

### 插件状态
- 已安装 marketplaces: 9 个 ✅
- 问题 marketplace: claude-code-marketplace

---

## 下一步操作

1. **选择合适的解决方案**（根据你的网络环境）
2. **应用配置**
3. **测试连接**
4. **重启 Claude Code**
5. **验证插件加载**

---

**需要帮助？** 告诉我你的网络环境（是否在中国、是否有代理等），我可以提供更具体的配置建议。
