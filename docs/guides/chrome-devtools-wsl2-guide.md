# Chrome DevTools WSL2 远程调试配置指南

## 📋 概述

**适用场景**: 在 WSL2 中运行的前端项目，需要从 Windows 侧使用 Chrome DevTools 调试。

**核心发现**: WSL2 和 Windows 的 localhost 不互通，必须使用 Windows 的物理网卡 IP 地址进行连接。

---

## 🔧 配置步骤

### 第一步：Windows 侧配置（一次性设置）

在 **Windows PowerShell (管理员)** 中执行以下命令：

```powershell
# 1. 定义 Chrome 路径（自动适配 32/64 位）
$chromePath = if (Test-Path "C:\Program Files\Google\Chrome\Application\chrome.exe") {
    "C:\Program Files\Google\Chrome\Application\chrome.exe"
} else {
    "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
}

# 2. 创建独立配置目录（避免影响主 Chrome 配置）
$profileDir = "$env:USERPROFILE\ChromeProfiles\mcp"
if (-not (Test-Path $profileDir)) {
    New-Item -ItemType Directory -Path $profileDir | Out-Null
}

# 3. 启动 Chrome（开启远程调试模式）
Start-Process -FilePath $chromePath -ArgumentList @(
    "--user-data-dir=`"$profileDir`"",
    "--remote-debugging-port=9230",
    "--remote-debugging-address=0.0.0.0",
    "--no-first-run",
    "--no-default-browser-check"
)

# 4. 添加防火墙规则（允许端口 9230）
New-NetFirewallRule -DisplayName "Chrome Remote Debugging 9230" `
    -Direction Inbound `
    -LocalPort 9230 `
    -Protocol TCP `
    -Action Allow `
    -Profile Domain,Public,Private
```

### 第二步：获取 Windows 物理网卡 IP

在 **Windows PowerShell** 中执行：

```powershell
# 获取所有网络适配器的 IPv4 地址
ipconfig | findstr "IPv4"
```

示例输出：
```
IPv4 Address. . . . . . . . . . . : 192.168.123.74
IPv4 Address. . . . . . . . . . . : 192.168.1.100
```

**选择物理网卡 IP**：通常是 `192.168.xxx.xxx` 格式的地址。

### 第三步：WSL2 侧测试连接

在 **WSL2 终端** 中执行：

```bash
# 假设 Windows IP 为 192.168.123.74
CHROME_IP="192.168.123.74"
CHROME_PORT="9230"

# 测试连接
curl http://${CHROME_IP}:${CHROME_PORT}/json
```

成功响应示例：
```json
[
  {
    "description": "",
    "devtoolsFrontendUrl": "/devtools/inspector.html?ws=localhost:9230/devtools/page/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    "id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    "title": "MyStocks 前端",
    "type": "page",
    "url": "http://localhost:3000/",
    "webSocketDebuggerUrl": "ws://localhost:9230/devtools/page/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
  }
]
```

---

## 🔍 访问方式对比分析

| 访问方式 | 结果 | 核心原因 | 推荐度 |
|----------|------|----------|--------|
| `10.255.255.254:9230` | ❌ 连接拒绝 | Windows 防火墙对 WSL2 NAT 网段的隐式拦截 | ❌ 不推荐 |
| `localhost:9230` | ❌ 连接拒绝 | WSL2 和 Windows 的 localhost 不互通 | ❌ 不推荐 |
| `192.168.123.74:9230` | ✅ **成功访问** | 直接访问物理网卡，绕过 NAT 拦截 | ✅ **强烈推荐** |

### 技术原因详解

#### 1. NAT 网关 IP 失败（10.255.255.254）
WSL2 使用 NAT 网络模式，Windows 防火墙对 NAT 网段（10.255.255.0/24）有额外的安全检查，即使添加了防火墙规则，仍可能被默认策略拦截。

#### 2. localhost 失败
WSL2 和 Windows 有独立的网络 namespace：
- WSL2 的 `localhost` → 仅指向 WSL2 自身（127.0.0.1）
- Windows 的 `localhost` → 仅指向 Windows 自身（127.0.0.1）
- 需要使用 IP 地址才能跨系统访问

#### 3. 物理网卡 IP 成功（192.168.123.74）
- Windows 防火墙对物理网卡网段的入站连接更为宽松
- Chrome 的 `--remote-debugging-address=0.0.0.0` 在物理网卡上正常生效
- 完全绕过了 NAT 网段的隐式拦截规则

---

## 🛠️ 使用方法

### 方法一：直接在 Chrome 中打开 DevTools

1. 在 Windows Chrome 中访问你的前端应用：
   ```
   http://localhost:3000/  (或你的前端端口)
   ```

2. 按 `F12` 或右键选择"检查"打开 DevTools

3. 现在可以在 Windows Chrome 中正常调试 WSL2 中的前端代码

### 方法二：使用 Chrome DevTools Protocol API

在 WSL2 中执行命令：

```bash
# 获取所有打开的页面
curl -s http://192.168.123.74:9230/json | python3 -m json.tool

# 获取 Chrome 版本信息
curl -s http://192.168.123.74:9230/json/version

# 打开新的调试页面（需要 URL 编码）
curl "http://192.168.123.74:9230/json/new?url=http%3A//localhost%3A3000"
```

### 方法三：自动化脚本

创建自动化连接脚本 `/opt/claude/mystocks_spec/scripts/dev/chrome-devtools-connect.sh`：

```bash
#!/bin/bash
# Chrome DevTools WSL2 连接脚本

# 配置参数
CHROME_IP="192.168.123.74"  # 请根据实际情况修改
CHROME_PORT="9230"

echo "=== Chrome DevTools 连接测试 ==="
echo "Chrome 地址: ${CHROME_IP}:${CHROME_PORT}"
echo

# 测试连接
echo "1. 测试连接..."
if curl -s --max-time 5 http://${CHROME_IP}:${CHROME_PORT}/json >/dev/null 2>&1; then
    echo "✅ Chrome DevTools 连接成功"
    echo

    # 获取页面列表
    echo "2. 获取页面列表..."
    curl -s http://${CHROME_IP}:${CHROME_PORT}/json | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f'发现 {len(data)} 个页面:')
for i, page in enumerate(data, 1):
    print(f'  {i}. {page.get(\"title\", \"Untitled\")} - {page.get(\"url\", \"No URL\")}')
    "
else
    echo "❌ 连接失败"
    echo "请检查："
    echo "  1. Windows 侧 Chrome 是否已启动远程调试模式"
    echo "  2. IP 地址是否正确：${CHROME_IP}"
    echo "  3. 防火墙是否允许端口 ${CHROME_PORT}"
    exit 1
fi
```

---

## ⚠️ 注意事项

### IP 地址变化
- **每次重启 Windows 后**，物理网卡 IP 可能发生变化
- **解决方案**：重新执行 `ipconfig | findstr "IPv4"` 获取最新 IP
- **建议**：将 IP 地址记录在项目的 `.env` 文件中

### 防火墙配置
- 确保防火墙规则包含所有配置文件：`Domain,Public,Private`
- 如果连接仍然失败，尝试重新添加防火墙规则

### Chrome 进程管理
- 使用独立的用户数据目录，避免影响主 Chrome 配置
- 可以同时运行多个 Chrome 实例用于不同目的

### 网络连接稳定性
- WSL2 和 Windows 的网络连接可能偶尔不稳定
- 如果连接断开，重新获取 IP 地址并重试

---

## 🚀 最佳实践

### 1. 项目配置
在项目根目录创建 `.env` 文件：
```bash
# Chrome DevTools 远程调试配置
CHROME_DEBUG_IP=192.168.123.74
CHROME_DEBUG_PORT=9230
```

### 2. 开发工作流
1. **Windows 侧**：启动带远程调试的 Chrome（一次性配置）
2. **WSL2 侧**：运行前端开发服务器
3. **Windows 侧**：打开前端页面，按 F12 开始调试
4. **日常开发**：直接在 Windows Chrome 中进行调试

### 3. 故障排除
如果连接失败，按以下顺序检查：
1. Windows Chrome 是否正在运行远程调试模式
2. IP 地址是否正确（重新获取）
3. 防火墙规则是否生效
4. 端口是否被其他程序占用

### 4. 高级用法
- 使用 Chrome DevTools Protocol 进行自动化测试
- 集成到 CI/CD 流水线进行前端调试
- 配合 VS Code 的 Debugger for Chrome 扩展

---

## 📚 相关文档

- **完整配置记录**: [`CLAUDE.md`](../CLAUDE.md) 第374-462行
- **成功报告**: `/tmp/chrome_devtools_success_report.md`
- **问题诊断**: `/tmp/ralph_loop_iteration_1.md`
- **修复过程**: `/tmp/ralph_loop_iteration_2.md`
- **最终总结**: `/tmp/FINAL_COMPLETION_REPORT.md`

---

**配置状态**: ✅ 已验证成功
**最后更新**: 2026-01-22
**适用环境**: WSL2 + Windows + Chrome</content>
<parameter name="filePath">docs/guides/CHROME_DEVTOOLS_WSL2_GUIDE.md