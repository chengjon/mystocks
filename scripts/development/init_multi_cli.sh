#!/bin/bash
# scripts/dev/init_multi_cli.sh - 一键初始化多CLI环境

set -e

# 注意：bash脚本中使用的是GNU time命令或sleep内置命令
# Python脚本中使用time标准库（已在前面的依赖安装部分说明）

echo "🚀 初始化多CLI协作环境 v2.0..."

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Step 1: 创建目录结构
echo -e "\n📁 ${YELLOW}创建目录结构...${NC}"
mkdir -p CLIS/main/{mailbox,archive,checkpoints}
mkdir -p CLIS/web/{mailbox,archive}
mkdir -p CLIS/api/{mailbox,archive}
mkdir -p CLIS/db/{mailbox,archive}
mkdir -p CLIS/it/worker{1..3}/{mailbox,archive}
mkdir -p CLIS/{locks,SHARED,templates}

echo -e "${GREEN}✅ 目录结构创建完成${NC}"

# Step 2: 复制模板文件
echo -e "\n📄 ${YELLOW}生成模板文件...${NC}"

# 生成模板文件
cat > CLIS/templates/TASK.md.template << 'TEMPLATEEOF'
# 任务清单

## 当前任务

当前无任务，等待main分配。

## 任务历史

| 任务ID | 任务名称 | 完成时间 | 状态 |
|--------|---------|---------|------|
TEMPLATEEOF

cat > CLIS/templates/RULES.md.template << 'TEMPLATEEOF'
# 工作规范

## 核心职责

（待main分配）

## 工作流程

1. 接收任务
2. 执行任务
3. 提交代码
4. 更新REPORT.md

## 沟通规范

- 通过mailbox进行异步通信
- 紧急问题使用ALERT类型消息
- 普通请求使用REQUEST类型消息
TEMPLATEEOF

cat > CLIS/templates/STATUS.md.template << 'TEMPLATEEOF'
# 当前状态

**CLI**: CLI-NAME
**Updated**: {{TIMESTAMP}}

## Current State

**State**: 🟢 Idle
**Current Task**: 无
**Progress**: N/A

## Blocked On

无

## Issues

无
TEMPLATEEOF

# 复制模板到各CLI目录
for cli in main web api db it/worker1 it/worker2 it/worker3; do
    cp CLIS/templates/TASK.md.template CLIS/$cli/TASK.md
    cp CLIS/templates/RULES.md.template CLIS/$cli/RULES.md
    cp CLIS/templates/STATUS.md.template CLIS/$cli/STATUS.md
    # 替换CLI-NAME占位符（使用|作为sed分隔符，避免路径中的/冲突）
    sed -i "s|CLI-NAME|$cli|g" CLIS/$cli/STATUS.md
    sed -i "s|{{TIMESTAMP}}|$(date '+%Y-%m-%d %H:%M:%S')|g" CLIS/$cli/STATUS.md
done

echo -e "${GREEN}✅ 模板文件生成完成${NC}"

# Step 3: 生成初始任务（从main开始）
echo -e "\n⚙️  ${YELLOW}生成初始任务...${NC}"

# 这里可以读取任务配置文件或使用默认任务
cat > CLIS/main/TASK.md << 'MAINTEOFE'
# CLI-main 初始任务

## 立即执行

### Phase 1: 修复关键阻塞
- [ ] 1.1 修复.env中的USE_MOCK_DATA配置
- [ ] 1.2 修复dashboard.py中的Mock依赖
- [ ] 1.3 修复导入路径

## 下一步

完成Phase 1后，为其他CLI分配任务。
MAINTEOFE

echo -e "${GREEN}✅ 初始任务生成完成${NC}"

# Step 4: 创建配置文件
echo -e "\n⚙️  ${YELLOW}创建配置文件...${NC}"

cat > CLIS/main/.cli_config << 'CONFOFE'
# CLI配置文件

[cli]
name = main
type = coordinator

[mailbox]
watcher_enabled = true
scan_interval = 60

[coordination]
auto_coordinate = true
coordinate_interval = 300
CONFOFE

for cli in web api db; do
    cat > CLIS/$cli/.cli_config << CONFOFE
[cli]
name = $cli
type = worker

[mailbox]
watcher_enabled = true
scan_interval = 60
CONFOFE
done

echo -e "${GREEN}✅ 配置文件创建完成${NC}"

# Step 5: 启动协调器（后台）
echo -e "\n🤖 ${YELLOW}启动CLI协调器...${NC}"

nohup python scripts/dev/smart_coordinator.py --auto >> CLIS/main/coordinator.log 2>&1 &
COORDINATOR_PID=$!
echo $COORDINATOR_PID > CLIS/main/.coordinator_pid

echo -e "${GREEN}✅ 协调器已启动 (PID: $COORDINATOR_PID)${NC}"

# Step 6: 提示启动mailbox监听器
echo -e "\n📬 ${YELLOW}Mailbox监听器启动提示...${NC}"
echo "每个CLI在启动时，请运行以下命令启动mailbox监听器："
echo ""
echo -e "${GREEN}python scripts/dev/mailbox_watcher.py --cli=main &${NC}"
echo -e "${GREEN}python scripts/dev/mailbox_watcher.py --cli=web &${NC}"
echo -e "${GREEN}python scripts/dev/mailbox_watcher.py --cli=api &${NC}"
echo -e "${GREEN}python scripts/dev/mailbox_watcher.py --cli=db &${NC}"
echo -e "${GREEN}python scripts/dev/mailbox_watcher.py --cli=it/worker1 &${NC}"
echo ""

# Step 7: 显示状态信息
echo -e "\n📊 ${YELLOW}初始化完成！${NC}"
echo ""
echo "下一步操作："
echo "1. 启动各CLI的mailbox监听器（见上）"
echo "2. 查看main任务: cat CLIS/main/TASK.md"
echo "3. 开始执行任务！"
echo ""
echo "监控命令："
echo "  查看状态: python scripts/dev/cli_coordinator.py --scan"
echo "  查看消息: ls CLIS/*/mailbox/"
echo "  停止协调器: kill $COORDINATOR_PID"
echo ""

echo -e "${GREEN}✅ 多CLI环境初始化完成！${NC}"
