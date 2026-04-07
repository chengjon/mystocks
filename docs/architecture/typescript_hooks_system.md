# TypeScript HOOKS质量门禁系统设计

> **参考指南说明**:
> 本文件是架构相关的补充指南、说明或笔记，不是当前仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现及主线治理文档一并核对。
>
> 文内步骤、示例和说明应视为补充参考；若与当前代码或主线治理文档冲突，应以 `architecture/STANDARDS.md`、当前代码实现及主线治理文档为准。


## 系统概述

HOOKS质量门禁系统在代码提交、合并等关键节点自动执行质量检查，确保只有符合质量标准的代码才能进入代码库，实现质量的最后防线。

## 核心架构

### 1. 门禁引擎 (Gate Engine)

#### 分层门禁设计

```typescript
export enum GateLevel {
  COMMIT = 'commit',        // 提交门禁
  PUSH = 'push',           // 推送门禁
  PR = 'pr',              // PR门禁
  MERGE = 'merge',         // 合并门禁
  RELEASE = 'release'      // 发布门禁
}

export class GateEngine {
  private gates: Map<GateLevel, QualityGate> = new Map()

  constructor() {
    this.initializeGates()
  }

  async checkGate(
    level: GateLevel,
    files: string[],
    options: GateOptions = {}
  ): Promise<GateResult> {
    const gate = this.gates.get(level)
    if (!gate) {
      throw new Error(`Gate level ${level} not configured`)
    }

    const result = await gate.check(files, options)

    if (!result.passed && gate.shouldBlock(level)) {
      await this.handleFailure(result, level, options)
    }

    return result
  }
}
```

#### 门禁配置系统

```typescript
export interface GateConfiguration {
  // 基础配置
  enabled: boolean
  level: GateLevel

  // 质量阈值
  thresholds: {
    typescript: number    // 0-100
    eslint: number       // 0-100
    custom: number       // 0-100
    overall: number      // 0-100
  }

  // 检查规则
  rules: {
    typescript: boolean
    eslint: boolean
    custom: boolean
    performance: boolean
    security: boolean
  }

  // 行为配置
  behavior: {
    blockOnFailure: boolean
    allowWarnings: boolean
    autoFix: boolean
    reportOnly: boolean
  }

  // 通知配置
  notifications: {
    onFailure: NotificationChannel[]
    onSuccess: NotificationChannel[]
    reportFormat: 'json' | 'markdown' | 'html'
  }
}
```

### 2. 检查执行器 (Check Executor)

#### 并行检查执行

```typescript
export class CheckExecutor {
  private checkers: QualityChecker[] = []

  async executeChecks(
    files: string[],
    config: GateConfiguration
  ): Promise<CheckResults> {
    // 并行执行所有检查器
    const promises = this.checkers
      .filter(checker => this.shouldRunChecker(checker, config))
      .map(checker => checker.check(files, config))

    const results = await Promise.allSettled(promises)

    // 聚合结果
    return this.aggregateResults(results)
  }

  private shouldRunChecker(
    checker: QualityChecker,
    config: GateConfiguration
  ): boolean {
    switch (checker.type) {
      case 'typescript':
        return config.rules.typescript
      case 'eslint':
        return config.rules.eslint
      case 'custom':
        return config.rules.custom
      default:
        return false
    }
  }

  private aggregateResults(results: PromiseSettledResult<CheckResult>[]): CheckResults {
    const aggregated: CheckResults = {
      typescript: { passed: true, score: 100, errors: [], warnings: [] },
      eslint: { passed: true, score: 100, errors: [], warnings: [] },
      custom: { passed: true, score: 100, errors: [], warnings: [] },
      overall: { passed: true, score: 100 }
    }

    results.forEach(result => {
      if (result.status === 'fulfilled') {
        const checkResult = result.value
        aggregated[checkResult.type] = checkResult

        // 更新总体分数
        aggregated.overall.score = Math.min(
          aggregated.overall.score,
          checkResult.score
        )

        // 如果任何检查失败，总体失败
        if (!checkResult.passed) {
          aggregated.overall.passed = false
        }
      } else {
        // 处理检查执行失败
        console.error('Check execution failed:', result.reason)
        aggregated.overall.passed = false
        aggregated.overall.score = 0
      }
    })

    return aggregated
  }
}
```

#### 增量检查优化

```typescript
export class IncrementalChecker {
  private lastCheckResults: Map<string, CheckResult> = new Map()
  private fileHashes: Map<string, string> = new Map()

  async checkIncrementally(
    files: string[],
    fullCheck: (files: string[]) => Promise<CheckResult>
  ): Promise<CheckResult> {
    const changedFiles = await this.identifyChangedFiles(files)

    if (changedFiles.length === 0) {
      // 没有文件变化，直接返回缓存结果
      return this.getCachedResult()
    }

    if (changedFiles.length === files.length) {
      // 所有文件都变化了，执行完整检查
      return await fullCheck(files)
    }

    // 只检查变更的文件
    const incrementalResult = await fullCheck(changedFiles)

    // 合并结果
    return this.mergeResults(incrementalResult, this.lastCheckResults)
  }

  private async identifyChangedFiles(files: string[]): Promise<string[]> {
    const changedFiles: string[] = []

    for (const file of files) {
      const currentHash = await this.calculateFileHash(file)
      const lastHash = this.fileHashes.get(file)

      if (currentHash !== lastHash) {
        changedFiles.push(file)
        this.fileHashes.set(file, currentHash)
      }
    }

    return changedFiles
  }
}
```

## 实现方案

### 1. Git Hooks集成

#### Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

echo "🔍 Running TypeScript Quality Gate (Pre-commit)..."

# 检查暂存的文件
STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACM | grep -E '\.(ts|tsx|vue)$')

if [ -z "$STAGED_FILES" ]; then
    echo "✅ No TypeScript files to check"
    exit 0
fi

# 运行质量检查
npx ts-quality-guard check --files "$STAGED_FILES" --gate commit

if [ $? -ne 0 ]; then
    echo "❌ Quality check failed. Please fix the issues before committing."
    echo "💡 Run 'npx ts-quality-guard check --fix' to auto-fix some issues"
    exit 1
fi

echo "✅ Quality check passed!"
```

#### Pre-push Hook

```bash
#!/bin/bash
# .git/hooks/pre-push

echo "🚀 Running TypeScript Quality Gate (Pre-push)..."

# 获取要推送的提交范围
while read local_ref local_sha remote_ref remote_sha
do
    if [ "$local_sha" = $z40 ]; then
        # 删除分支
        exit 0
    else
        # 检查提交范围
        COMMIT_RANGE="$remote_sha..$local_sha"
    fi
done

# 获取变更的文件
CHANGED_FILES=$(git diff --name-only $COMMIT_RANGE | grep -E '\.(ts|tsx|vue)$')

if [ -z "$CHANGED_FILES" ]; then
    echo "✅ No TypeScript files to check"
    exit 0
fi

# 运行质量检查
npx ts-quality-guard check --files "$CHANGED_FILES" --gate push

if [ $? -ne 0 ]; then
    echo "❌ Quality check failed. Please fix the issues before pushing."
    exit 1
fi

echo "✅ Quality check passed!"
```

#### Commit-msg Hook

```bash
#!/bin/bash
# .git/hooks/commit-msg

COMMIT_MSG_FILE=$1
COMMIT_MSG=$(cat $COMMIT_MSG_FILE)

# 检查提交信息格式
if ! echo "$COMMIT_MSG" | grep -qE "^(feat|fix|docs|style|refactor|test|chore)(\(.+\))?: .{1,}"; then
    echo "❌ Invalid commit message format"
    echo "📝 Expected: type(scope): description"
    echo "📝 Example: feat(auth): add JWT token validation"
    exit 1
fi

echo "✅ Commit message format is valid"
```

### 2. CI/CD集成

#### GitHub Actions工作流

```yaml
name: TypeScript Quality Gate

on:
  pull_request:
    branches: [main, develop]
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  quality-gate:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        node-version: [18, 20]

    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Setup Node.js ${{ matrix.node-version }}
        uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Run TypeScript Quality Check
        id: quality-check
        run: |
          npx ts-quality-guard check --ci --threshold 85 --format json > quality-result.json
        continue-on-error: true

      - name: Upload quality report
        uses: actions/upload-artifact@v4
        with:
          name: quality-report-${{ matrix.node-version }}
          path: quality-result.json

      - name: Quality Gate Decision
        run: |
          SCORE=$(jq '.overall.score' quality-result.json)
          THRESHOLD=85

          if [ $(echo "$SCORE < $THRESHOLD" | bc -l) -eq 1 ]; then
            echo "❌ Quality score $SCORE is below threshold $THRESHOLD"
            echo "📊 See quality report for details"
            exit 1
          else
            echo "✅ Quality score $SCORE meets threshold $THRESHOLD"
          fi

      - name: Comment PR with quality report
        if: github.event_name == 'pull_request'
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs')
            const report = JSON.parse(fs.readFileSync('quality-result.json', 'utf8'))

            const comment = `
            ## 🔍 TypeScript Quality Report

            ### 📊 Overall Score: ${report.overall.score}/100

            | Check Type | Score | Status |
            |------------|-------|--------|
            | TypeScript | ${report.typescript.score}/100 | ${report.typescript.passed ? '✅' : '❌'} |
            | ESLint | ${report.eslint.score}/100 | ${report.eslint.passed ? '✅' : '❌'} |
            | Custom Rules | ${report.custom.score}/100 | ${report.custom.passed ? '✅' : '❌'} |

            ### 📋 Issues Found
            ${report.overall.errors.length > 0 ?
              report.overall.errors.slice(0, 10).map(err => `- ${err.file}:${err.line} ${err.message}`).join('\n') :
              'No critical issues found 🎉'
            }

            ${report.overall.errors.length > 10 ? `\n... and ${report.overall.errors.length - 10} more issues` : ''}
            `

            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: comment
            })
```

#### GitLab CI配置

```yaml
stages:
  - quality
  - test
  - deploy

typescript_quality_gate:
  stage: quality
  image: node:18
  before_script:
    - npm ci
  script:
    - npx ts-quality-guard check --ci --threshold 85 --format junit > quality-report.xml
  artifacts:
    reports:
      junit: quality-report.xml
    expire_in: 1 week
  only:
    - merge_requests
  allow_failure: false

typescript_quality_gate:blocking:
  extends: typescript_quality_gate
  script:
    - npx ts-quality-guard check --ci --threshold 90 --block-on-any-warning
  only:
    - main
    - develop
```

#### Jenkins Pipeline

```groovy
pipeline {
    agent any

    stages {
        stage('Quality Gate') {
            steps {
                script {
                    // 安装依赖
                    sh 'npm ci'

                    // 运行质量检查
                    def result = sh(
                        script: 'npx ts-quality-guard check --ci --threshold 85 --format json',
                        returnStdout: true
                    )

                    // 解析结果
                    def qualityReport = readJSON text: result

                    // 检查阈值
                    if (qualityReport.overall.score < 85) {
                        error "Quality score ${qualityReport.overall.score} is below threshold 85"
                    }

                    // 发布报告
                    publishHTML([
                        allowMissing: false,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: '.',
                        reportFiles: 'quality-report.html',
                        reportName: 'TypeScript Quality Report'
                    ])
                }
            }
        }
    }

    post {
        always {
            // 清理工作空间
            cleanWs()
        }
        failure {
            // 发送通知
            emailext(
                subject: "Quality Gate Failed: ${currentBuild.fullDisplayName}",
                body: "Quality check failed. Please check the build logs for details.",
                recipientProviders: [[$class: 'DevelopersRecipientProvider']]
            )
        }
    }
}
```

### 3. 报告系统 (Reporting System)

#### 质量报告生成器

```typescript
export class ReportGenerator {
  async generateReport(
    results: CheckResults,
    options: ReportOptions
  ): Promise<QualityReport> {
    const report: QualityReport = {
      timestamp: new Date().toISOString(),
      project: options.project,
      branch: options.branch,
      commit: options.commit,

      // 总体评估
      overall: {
        score: results.overall.score,
        passed: results.overall.passed,
        grade: this.calculateGrade(results.overall.score)
      },

      // 详细检查结果
      checks: {
        typescript: this.formatCheckResult(results.typescript),
        eslint: this.formatCheckResult(results.eslint),
        custom: this.formatCheckResult(results.custom)
      },

      // 问题汇总
      issues: this.aggregateIssues(results),

      // 改进建议
      recommendations: this.generateRecommendations(results),

      // 趋势分析
      trends: await this.analyzeTrends(options.project)
    }

    return report
  }

  private calculateGrade(score: number): string {
    if (score >= 95) return 'A+'
    if (score >= 90) return 'A'
    if (score >= 85) return 'B+'
    if (score >= 80) return 'B'
    if (score >= 75) return 'C+'
    if (score >= 70) return 'C'
    if (score >= 60) return 'D'
    return 'F'
  }

  private formatCheckResult(result: CheckResult): FormattedCheckResult {
    return {
      score: result.score,
      passed: result.passed,
      errors: result.errors.length,
      warnings: result.warnings.length,
      topIssues: result.errors.slice(0, 5).map(err => ({
        file: err.file,
        line: err.line,
        message: err.message,
        severity: err.severity
      }))
    }
  }

  private aggregateIssues(results: CheckResults): AggregatedIssues {
    const allErrors = [
      ...results.typescript.errors,
      ...results.eslint.errors,
      ...results.custom.errors
    ]

    const allWarnings = [
      ...results.typescript.warnings,
      ...results.eslint.warnings,
      ...results.custom.warnings
    ]

    return {
      errors: allErrors.length,
      warnings: allWarnings.length,
      byFile: this.groupByFile(allErrors),
      byType: this.groupByType(allErrors),
      bySeverity: this.groupBySeverity([...allErrors, ...allWarnings])
    }
  }

  private generateRecommendations(results: CheckResults): Recommendation[] {
    const recommendations: Recommendation[] = []

    // TypeScript相关建议
    if (results.typescript.score < 80) {
      recommendations.push({
        category: 'typescript',
        priority: 'high',
        title: '修复TypeScript类型错误',
        description: '存在未解决的类型错误，可能导致运行时问题',
        actions: [
          '查看具体错误信息',
          '添加缺失的类型注解',
          '修复导入路径问题'
        ]
      })
    }

    // ESLint相关建议
    if (results.eslint.score < 85) {
      recommendations.push({
        category: 'code-quality',
        priority: 'medium',
        title: '改进代码质量',
        description: 'ESLint检查发现代码质量问题',
        actions: [
          '运行ESLint自动修复',
          '检查代码风格一致性',
          '修复潜在的bug'
        ]
      })
    }

    // 自定义规则建议
    if (results.custom.score < 90) {
      recommendations.push({
        category: 'project-standards',
        priority: 'medium',
        title: '遵循项目规范',
        description: '未完全遵守项目的质量标准',
        actions: [
          '查看项目规范文档',
          '修复不符合规范的代码',
          '与团队确认标准理解'
        ]
      })
    }

    return recommendations
  }
}
```

#### 多格式报告输出

```typescript
export class ReportFormatter {
  format(report: QualityReport, format: ReportFormat): string {
    switch (format) {
      case 'json':
        return JSON.stringify(report, null, 2)

      case 'markdown':
        return this.formatMarkdown(report)

      case 'html':
        return this.formatHTML(report)

      case 'junit':
        return this.formatJUnit(report)

      default:
        throw new Error(`Unsupported format: ${format}`)
    }
  }

  private formatMarkdown(report: QualityReport): string {
    return `
# 🔍 TypeScript Quality Report

**Generated**: ${report.timestamp}
**Project**: ${report.project}
**Branch**: ${report.branch}
**Commit**: ${report.commit}

## 📊 Overall Assessment

- **Score**: ${report.overall.score}/100
- **Grade**: ${report.overall.grade}
- **Status**: ${report.overall.passed ? '✅ PASSED' : '❌ FAILED'}

## 📋 Check Results

| Check Type | Score | Status | Errors | Warnings |
|------------|-------|--------|--------|----------|
| TypeScript | ${report.checks.typescript.score} | ${report.checks.typescript.passed ? '✅' : '❌'} | ${report.checks.typescript.errors} | ${report.checks.typescript.warnings} |
| ESLint | ${report.checks.eslint.score} | ${report.checks.eslint.passed ? '✅' : '❌'} | ${report.checks.eslint.errors} | ${report.checks.eslint.warnings} |
| Custom Rules | ${report.checks.custom.score} | ${report.checks.custom.passed ? '✅' : '❌'} | ${report.checks.custom.errors} | ${report.checks.custom.warnings} |

## 🚨 Top Issues

${report.checks.typescript.topIssues.map(issue =>
  `- **${issue.file}:${issue.line}** ${issue.message}`
).join('\n')}

## 💡 Recommendations

${report.recommendations.map(rec =>
  `### ${rec.priority.toUpperCase()}: ${rec.title}\n${rec.description}\n\n**Actions:**\n${rec.actions.map(action => `- ${action}`).join('\n')}`
).join('\n\n')}

## 📈 Trends

${this.formatTrends(report.trends)}
    `.trim()
  }
}
```

## 通知系统

### 1. 多渠道通知

```typescript
export class NotificationSystem {
  private channels: NotificationChannel[] = []

  async sendNotification(
    report: QualityReport,
    config: NotificationConfig
  ): Promise<void> {
    const notifications = this.generateNotifications(report, config)

    await Promise.all(
      notifications.map(notification =>
        this.sendToChannel(notification)
      )
    )
  }

  private generateNotifications(
    report: QualityReport,
    config: NotificationConfig
  ): Notification[] {
    const notifications: Notification[] = []

    // 失败通知
    if (!report.overall.passed && config.notifyOnFailure) {
      notifications.push({
        type: 'failure',
        title: `❌ Quality Gate Failed: ${report.project}`,
        message: `Score: ${report.overall.score}/100, Grade: ${report.overall.grade}`,
        details: report,
        channels: config.failureChannels
      })
    }

    // 成功通知
    if (report.overall.passed && config.notifyOnSuccess) {
      notifications.push({
        type: 'success',
        title: `✅ Quality Gate Passed: ${report.project}`,
        message: `Score: ${report.overall.score}/100, Grade: ${report.overall.grade}`,
        details: report,
        channels: config.successChannels
      })
    }

    // 阈值警告
    if (report.overall.score < config.warningThreshold) {
      notifications.push({
        type: 'warning',
        title: `⚠️ Quality Gate Warning: ${report.project}`,
        message: `Score ${report.overall.score} is below warning threshold ${config.warningThreshold}`,
        details: report,
        channels: config.warningChannels
      })
    }

    return notifications
  }
}

export interface NotificationChannel {
  type: 'slack' | 'discord' | 'email' | 'webhook' | 'console'
  config: ChannelConfig

  send(notification: Notification): Promise<void>
}
```

### 2. Slack集成

```typescript
export class SlackChannel implements NotificationChannel {
  type = 'slack' as const

  async send(notification: Notification): Promise<void> {
    const payload = {
      channel: this.config.channel,
      username: 'TypeScript Quality Guard',
      icon_emoji: notification.type === 'failure' ? ':x:' : ':white_check_mark:',
      attachments: [{
        color: this.getColor(notification.type),
        title: notification.title,
        text: notification.message,
        fields: this.formatFields(notification.details),
        footer: 'TypeScript Quality Guard',
        ts: Date.now() / 1000
      }]
    }

    await fetch(this.config.webhookUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
  }

  private getColor(type: NotificationType): string {
    switch (type) {
      case 'failure': return 'danger'
      case 'warning': return 'warning'
      case 'success': return 'good'
      default: return '#808080'
    }
  }
}
```

## 性能监控

### 1. 门禁性能指标

```typescript
export class PerformanceMonitor {
  private metrics: PerformanceMetrics = {
    checkDuration: [],
    memoryUsage: [],
    cpuUsage: [],
    cacheHitRate: 0
  }

  startMonitoring(): void {
    this.monitorInterval = setInterval(() => {
      this.collectMetrics()
    }, 1000)
  }

  private async collectMetrics(): Promise<void> {
    // 收集检查持续时间
    const checkDuration = performance.now() - this.lastCheckStart
    this.metrics.checkDuration.push(checkDuration)

    // 收集内存使用
    const memUsage = process.memoryUsage()
    this.metrics.memoryUsage.push(memUsage.heapUsed)

    // 收集CPU使用率
    const cpuUsage = await this.getCpuUsage()
    this.metrics.cpuUsage.push(cpuUsage)

    // 保持最近100个数据点
    this.trimMetrics()
  }

  getPerformanceReport(): PerformanceReport {
    return {
      averageCheckDuration: this.average(this.metrics.checkDuration),
      maxCheckDuration: Math.max(...this.metrics.checkDuration),
      averageMemoryUsage: this.average(this.metrics.memoryUsage),
      maxMemoryUsage: Math.max(...this.metrics.memoryUsage),
      averageCpuUsage: this.average(this.metrics.cpuUsage),
      cacheHitRate: this.metrics.cacheHitRate,
      recommendations: this.generateRecommendations()
    }
  }

  private generateRecommendations(): string[] {
    const recommendations: string[] = []

    if (this.average(this.metrics.checkDuration) > 5000) {
      recommendations.push('考虑启用增量检查以提高性能')
    }

    if (this.average(this.metrics.memoryUsage) > 200 * 1024 * 1024) {
      recommendations.push('内存使用较高，考虑优化缓存策略')
    }

    if (this.average(this.metrics.cpuUsage) > 50) {
      recommendations.push('CPU使用率较高，考虑减少并行检查数量')
    }

    return recommendations
  }
}
```

## 总结

HOOKS质量门禁系统通过以下核心特性实现了代码质量的最后防线：

### 核心优势
1. **自动化检查**: 在关键节点自动执行质量验证
2. **多层防护**: 从提交到发布的全流程质量控制
3. **并行执行**: 多检查器并行，提高效率
4. **增量优化**: 只检查变更的文件，性能优异

### 技术亮点
1. **Git Hooks集成**: 无缝集成到开发工作流
2. **CI/CD支持**: 支持主流CI/CD平台
3. **多格式报告**: 支持多种报告格式和通知渠道
4. **性能监控**: 实时监控和优化系统性能

### 业务价值
1. **质量保障**: 确保只有高质量代码进入主分支
2. **提前发现**: 在代码合并前发现和修复问题
3. **流程标准化**: 统一的质量检查流程和标准
4. **成本控制**: 避免生产环境的质量问题

### 实施效果预期
- **错误拦截率**: >95%的质量问题在提交前被拦截
- **修复效率**: 从数小时的code review减少到分钟级的自动化检查
- **团队效率**: 开发人员可以将更多精力投入业务逻辑
- **代码质量**: 显著提升整体代码质量和可维护性

这个HOOKS质量门禁系统将成为TypeScript项目质量保障的最后防线，确保代码质量从源头到发布的全流程控制。</content>
<parameter name="filePath">docs/architecture/typescript_hooks_system.md