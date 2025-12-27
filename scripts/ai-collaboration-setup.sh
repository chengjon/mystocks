#!/bin/bash
# AI 协作环境快速设置脚本
# 用途: 在不同的 CLI 中启动不同的 AI 工作环境

set -e

PROJECT_ROOT="/opt/claude/mystocks_spec"
PHASE4_DIR="../mystocks_phase4_polish"
PHASE5_DIR="../mystocks_phase5_planning"

echo "======================================"
echo "  AI 协作环境快速设置"
echo "======================================"
echo ""

# 检查 worktrees 是否存在
check_worktree() {
    local dir=$1
    local name=$2

    if [ -d "$dir" ]; then
        echo "✅ $name worktree 已存在: $dir"
        return 0
    else
        echo "❌ $name worktree 不存在: $dir"
        return 1
    fi
}

# 验证所有 worktrees
check_worktree "$PROJECT_ROOT" "主目录 (main)" || exit 1
check_worktree "/opt/claude/mystocks_phase4_polish" "Phase 4 (phase4-polish)" || exit 1
check_worktree "/opt/claude/mystocks_phase5_planning" "Phase 5 (phase5-planning)" || exit 1

echo ""
echo "======================================"
echo "  选择要启动的 AI 环境"
echo "======================================"
echo ""
echo "1) AI 1: GEMINI (Phase 4 测试修复)"
echo "   目录: $PHASE4_DIR"
echo "   分支: phase4-polish"
echo "   任务: 修复剩余 13 个测试失败 (90.8% → 95%+)"
echo ""
echo "2) AI 2: OPENCODE (Phase 5 需求设计)"
echo "   目录: $PHASE5_DIR"
echo "   分支: phase5-planning"
echo "   任务: 需求分析、架构设计、API 设计"
echo ""
echo "3) AI 3: Claude (主协调 + 前端)"
echo "   目录: $PROJECT_ROOT"
echo "   分支: main"
echo "   任务: 协调工作、前端开发支持、代码审查"
echo ""
read -p "请选择 [1-3]: " choice

case $choice in
    1)
        echo ""
        echo "🚀 启动 AI 1 环境 (GEMINI + Phase 4)..."
        echo "工作目录: $(cd "$PHASE4_DIR" && pwd)"
        echo "当前分支: $(cd "$PHASE4_DIR" && git branch --show-current)"
        echo ""
        echo "📋 待完成任务:"
        echo "  - 修复 Bollinger Bands null/NaN 问题（6个测试）"
        echo "  - 修复 EMA/OBV 长度不匹配（2个测试）"
        echo "  - 修复 RSI 参数验证（1个测试）"
        echo "  - 修复 KDJ 值范围（1个测试）"
        echo "  - 修复类型安全测试（1个测试）"
        echo "  - 修复布林带价格包含测试（1个测试）"
        echo "  - 修复数据类型测试（1个测试）"
        echo ""
        echo "💡 提示: 在新 CLI 中执行以下命令进入工作目录:"
        echo "   cd $PHASE4_DIR"
        echo "   claude  # 或其他 AI CLI"
        ;;
    2)
        echo ""
        echo "🚀 启动 AI 2 环境 (OPENCODE + Phase 5)..."
        echo "工作目录: $(cd "$PHASE5_DIR" && pwd)"
        echo "当前分支: $(cd "$PHASE5_DIR" && git branch --show-current)"
        echo ""
        echo "📋 待完成任务:"
        echo "  - Phase 5 需求收集和分析"
        echo "  - 技术选型和架构设计"
        echo "  - API Schema 设计"
        echo "  - 数据库设计"
        echo ""
        echo "💡 提示: 在新 CLI 中执行以下命令进入工作目录:"
        echo "   cd $PHASE5_DIR"
        echo "   claude  # 或其他 AI CLI"
        ;;
    3)
        echo ""
        echo "🚀 启动 AI 3 环境 (Claude + 主协调)..."
        echo "工作目录: $PROJECT_ROOT"
        echo "当前分支: $(cd "$PROJECT_ROOT" && git branch --show-current)"
        echo ""
        echo "📋 主要任务:"
        echo "  - 协调 AI 1 和 AI 2 的工作"
        echo "  - 前端组件开发支持"
        echo "  - 代码审查和质量保证"
        echo "  - 更新进度文件 .ai-progress.md"
        echo ""
        echo "💡 提示: 已在主目录，直接使用即可"
        ;;
    *)
        echo "❌ 无效选择"
        exit 1
        ;;
esac

echo ""
echo "======================================"
echo "  协作提示"
echo "======================================"
echo ""
echo "📡 沟通方式:"
echo "  - Git Commit: 每完成一个功能就 git push"
echo "  - 进度文件: 更新 .ai-progress.md 并提交"
echo "  - 代码合并: 需要时使用 git merge 合并其他 AI 的代码"
echo ""
echo "🔄 每日工作流程:"
echo "  1. git fetch mystocks  # 拉取最新代码"
echo "  2. git log --oneline -5  # 查看最近提交"
echo "  3. ... 编写代码 ..."
echo "  4. git add . && git commit && git push"
echo "  5. 更新 .ai-progress.md"
echo ""
echo "📚 参考文档:"
echo "  - 协作规范: .ai-collaboration.md"
echo "  - 进度追踪: .ai-progress.md"
echo ""
