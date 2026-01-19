# E2E测试命令速查表

## 环境检查

```bash
# 验证E2E框架设置
bash tests/e2e/validate-e2e-setup.sh

# 检查服务器状态
lsof -i :3000 -i :8000 | grep LISTEN
```

## 测试执行

### 运行所有E2E测试
```bash
npx playwright test e2e
```

### 运行认证测试
```bash
npx playwright test e2e/auth.spec.ts
```

### 运行单个测试用例
```bash
npx playwright test e2e/auth.spec.ts -g "管理员账号登录成功"
```

### 运行带标签的测试
```bash
npx playwright test e2e --grep "@smoke"
npx playwright test e2e --grep "@critical"
npx playwright test e2e --grep "@validation"
```

## 调试模式

### UI模式（推荐）
```bash
npx playwright test e2e --ui
```

### 调试模式
```bash
npx playwright test e2e --debug
```

### 显示浏览器
```bash
npx playwright test e2e --headed
```

## 报告

### 查看HTML报告
```bash
npx playwright show-report
```

### 生成JSON报告
```bash
npx playwright test e2e --reporter=json
```

### 多种报告格式
```bash
npx playwright test e2e --reporter=html,json,line
```

## 交互式菜单

```bash
# 启动交互式测试菜单
bash scripts/run-e2e-tests.sh
```

## 测试特定浏览器

```bash
# 仅Chromium
npx playwright test e2e --project=e2e

# 仅Firefox
npx playwright test e2e --project=e2e-firefox

# 仅WebKit
npx playwright test e2e --project=e2e-webkit
```

## 其他选项

```bash
# 并行运行（默认）
npx playwright test e2e --workers=4

# 串行运行
npx playwright test e2e --workers=1

# 详细输出
npx playwright test e2e --reporter=list

# 失败时重试
npx playwright test e2e --retries=2
```

## Trace文件

```bash
# 查看trace
npx playwright show-trace test-results/*/trace.zip

# 记录所有测试的trace
npx playwright test e2e --trace on
```

## 快速验证

```bash
# 验证单个测试
npx playwright test e2e/auth.spec.ts -g "登录页面应该正确加载" --reporter=line

# 验证冒烟测试
npx playwright test e2e --grep "@smoke" --reporter=line
```

---

**提示**: 使用 `bash scripts/run-e2e-tests.sh` 获取交互式菜单，更易使用！
