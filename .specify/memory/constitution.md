通用项目宪法（融合版）

文档信息

创建人: JohnC
版本: 1.0.1
批准日期: 2025-10-09
最后修订: 2025-10-25
修订说明: 优化文档结构，精炼核心原则，增强可操作性，建立完整的质量保障体系
一、核心设计原则

1. 配置驱动原则

定义: 系统所有可变参数必须通过配置管理，实现业务逻辑与配置数据分离。

具体要求:

配置规范:
使用 YAML/JSON 格式，统一存放于 config/ 目录
敏感信息通过环境变量管理，禁止提交至版本库
配置变更需记录版本、变更原因和影响范围
生效机制:
配置中心统一管理，支持热更新
表结构通过配置自动生成，禁止手动 DDL
变更流程: 版本控制 → 测试验证 → 灰度发布 → 监控观察
2. 数据分类存储原则

定义: 基于数据特性和访问模式选择最优存储方案。

存储选型矩阵:

数据类型	访问特征	推荐存储	示例
实时数据	高频写入，低延迟查询	TDengine、Redis	行情Tick数据
关系数据	事务性，复杂查询	PostgreSQL、MySQL	用户信息、订单
文档数据	灵活Schema，快速开发	MongoDB	系统配置、日志
缓存数据	高速读写，临时存储	Redis	会话、热点数据
3. 分层架构原则

层级职责边界:

text

┌─────────────────┐

│   服务层       │ - 业务逻辑编排，API暴露

├─────────────────┤

│   处理层       │ - 数据清洗、转换、计算

├─────────────────┤

│   存储层       │ - 数据持久化，读写分离

├─────────────────┤

│   采集层       │ - 数据获取，格式验证

└─────────────────┘

依赖规则: 严格单向依赖，禁止跨层调用。

4. 智能路由原则

核心机制:

python

class DataRouter:

    def route_data(self, data: DataObject) -> StorageEngine:

        """基于数据分类自动选择存储引擎"""

       classification = self.classify_data(data)

        return self.routing_rules[classification]

统一接口: 所有数据操作通过 DataManager 统一入口，屏蔽底层差异。

5. 完整可观测性原则

监控体系:

性能监控: 响应时间、吞吐量、资源利用率
数据质量: 完整性、准确性、时效性
业务监控: 关键指标、 SLA 达成率
审计日志: 操作追踪、安全合规
技术指标:

Redis访问: P95 < 10ms
时序查询: 10万条数据 < 100ms
数据采集: 支持1000+并发
6. 安全容错原则

安全要求:

凭证集中管理，定期轮换
最小权限原则，操作审计
输入验证，输出过滤
容错机制:

断路器模式，防止级联故障
指数退避重试，最大5次
数据补偿，保证最终一致性
快速回滚，分钟级恢复
二、开发实施规范

1. 文档标准

文档类型矩阵:

文档类型	受众	核心内容	更新时机
需求文档	产品、开发	业务背景、功能清单	需求变更
设计文档	开发、架构	技术方案、接口设计	架构调整
API文档	开发、测试	接口规范、示例	接口变更
部署文档	运维、开发	环境配置、操作指南	环境变化
API文档示例:

markdown

### 获取日线数据

**端点**: `GET /api/market/daily`

**参数**:

```json

{

 "asset_code": "string, 必填",

 "start_date": "string, 格式YYYY-MM-DD",

 "end_date": "string, 格式YYYY-MM-DD"

}

响应:

json

{

  "code": 200,

  "data": [

    {

      "date": "2025-10-09",

      "open": 12.5,

      "close": 12.8,

      "volume": 1560000

    }

  ]

}

text

 

### 2. 代码规范

**文件结构**:

project/
├── core/ # 核心框架
│ ├── config/ # 配置管理
│ ├── router/ # 数据路由
│ └── monitor/ # 监控告警
├── business/ # 业务模块
│ ├── data_crawl/ # 数据采集
│ ├── data_process/ # 数据处理
│ └── trade/ # 交易相关
├── common/ # 公共组件
├── storage/ # 存储抽象
├── tests/ # 测试用例
└── docs/ # 项目文档

text

 

**代码质量标准**:

- Python ≥ 3.8，遵循 PEP8

- 类型注解覆盖率 ≥ 90%

- 函数圈复杂度 ≤ 10

- 代码重复率 ≤ 5%



### 3. 文件组织规范

**核心原则**: 保持根目录简洁，按功能逻辑分类，每个文件都有明确的规则位置。

**根目录标准**:

根目录**只允许**以下5个核心文件:
- `README.md` - 项目总览和主要文档
- `CLAUDE.md` - Claude Code集成指南
- `CHANGELOG.md` - 版本历史和变更记录
- `requirements.txt` - Python依赖
- `.mcp.json` - MCP服务器配置

**所有其他文件必须组织到子目录中**。

**目录结构与规则**:

1. **scripts/** - 所有可执行脚本

   按功能分为4类:

   **scripts/tests/** - 测试文件
   - 模式: 文件名以`test_`开头
   - 用途: 单元测试、集成测试、验收测试
   - 特殊文件: `test_requirements.txt`, `coverage.xml`

   **scripts/runtime/** - 生产运行脚本
   - 模式: 文件名以`run_`、`save_`、`monitor_`开头,或以`*_demo.py`结尾
   - 用途: 生产数据采集、监控、系统演示

   **scripts/database/** - 数据库操作
   - 模式: 文件名以`check_`、`verify_`、`create_`开头
   - 用途: 数据库初始化、验证、管理

   **scripts/dev/** - 开发工具
   - 模式: 不适合其他类别的开发实用工具
   - 用途: 代码验证、测试工具、开发辅助
   - 特殊文件: `git_commit_comments.txt`

2. **docs/** - 文档文件

   **docs/guides/** - 用户与开发者指南
   - 文件: `QUICKSTART.md`, `IFLOW.md`, 教程文档
   - 用途: 快速入门指南、工作流程文档

   **docs/archived/** - 废弃文档
   - 文件: `START_HERE.md`, `TASKMASTER_START_HERE.md`(保留用于历史参考)
   - 用途: 保留旧文档而不影响活动文档
   - 规则: 归档时在文件顶部添加废弃声明

   **docs/architecture/** - 架构设计文档
   - 用途: 系统设计、技术架构文档

   **docs/api/** - API文档
   - 用途: API参考、端点文档、SDK指南

3. **config/** - 配置文件

   **所有配置文件**(无论扩展名):
   - 扩展名: `.yaml`, `.yml`, `.ini`, `.toml`, `docker-compose.*.yml`
   - 示例:
     - `mystocks_table_config.yaml` - 表结构定义
     - `docker-compose.tdengine.yml` - Docker设置
     - `pytest.ini` - 测试配置
     - `.readthedocs.yaml` - 文档构建配置

4. **reports/** - 生成的报告和分析

   模式: 分析脚本生成的文件,如果定期生成则添加时间戳
   - 扩展名: `.json`, `.txt`, 分析输出
   - 示例:
     - `database_assessment_20251019_165817.json`
     - `query_patterns_analysis.txt`
     - `dump_result.txt`
   - 命名规范: 时间戳文件使用ISO日期格式: `YYYYMMDD_HHMMSS`

**文件生命周期管理**:

**前分类(主动式)**:

创建新文件时,直接放在正确位置:

1. 确定文件用途: 测试?运行?配置?文档?
2. 匹配规则: 使用上述目录结构
3. 在正确位置创建: 除非是5个核心文件之一,否则不要在根目录创建

示例:
```python
# ✅ 正确: 直接在scripts/tests/创建
with open('scripts/tests/test_new_feature.py', 'w') as f:
    f.write(test_code)

# ❌ 错误: 在根目录创建
with open('test_new_feature.py', 'w') as f:
    f.write(test_code)
```

**后分类(反应式)**:

整理现有文件时:

1. 识别错位文件: 使用`ls`或`find`列出根目录文件
2. 按规则分类: 根据上述目录结构规则匹配每个文件
3. 规划重组: 执行前制定分类计划
4. 使用git mv: 移动已跟踪文件时保留历史记录
5. 更新引用: 更新所有导入路径、文档链接
6. 验证: 测试移动后的文件正常工作

后分类工作流:
```bash
# 1. 列出根目录文件(排除核心5个)
ls -1 | grep -v -E '^(README\.md|CLAUDE\.md|CHANGELOG\.md|requirements\.txt|\.mcp\.json)$'

# 2. 根据上述规则确定每个文件的正确位置

# 3. 移动文件(已跟踪文件使用git mv)
git mv test_something.py scripts/tests/
git mv run_collector.py scripts/runtime/
git mv config.yaml config/
git mv analysis_report.txt reports/

# 4. 更新受影响文件中的引用

# 5. 使用描述性消息提交
git commit -m "refactor: 按目录结构规则组织文件"
```

**脚本导入路径管理**:

关键规则: `scripts/**/`中的所有脚本必须正确计算项目根目录。

标准模式:
```python
import sys
import os
from pathlib import Path

# 计算项目根目录(从脚本位置向上3级)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

# 现在可以从项目根目录导入
from core import ConfigDrivenTableManager
from adapters.akshare_adapter import AkshareDataSource
from db_manager.database_manager import DatabaseTableManager
```

**Git最佳实践**:

已跟踪文件始终使用`git mv`:
```bash
# ✅ 正确: 保留文件历史
git mv old_location/file.py new_location/file.py

# ❌ 错误: 破坏文件历史
mv old_location/file.py new_location/file.py
git add new_location/file.py
```

**验证清单**:

任何文件重组后:

- [ ] 根目录只包含5个核心文件
- [ ] 所有脚本正确分类在scripts/{tests,runtime,database,dev}
- [ ] 所有文档在docs/{guides,archived,architecture,api}
- [ ] 所有配置文件在config/
- [ ] 所有报告在reports/
- [ ] 所有移动的脚本已更新导入路径(3级dirname)
- [ ] 所有文档链接更新到新路径
- [ ] `git status`显示移动(不是删除+添加)
- [ ] 重组后所有测试通过
- [ ] `scripts/README.md`已更新

**常见错误**:

1. 在根目录创建文件: 除非是5个核心文件之一,否则始终使用子目录
2. 错误的导入路径: 记得为嵌套目录中的脚本使用3级dirname
3. 使用`mv`而不是`git mv`: 始终保留git历史记录
4. 忘记更新引用: 检查所有导入、文档链接
5. 混合用途: 不要将测试文件放在runtime/,或将配置文件放在docs/

**参考文档**:

- 完整文档结构: 参见`docs/DOCUMENTATION_STRUCTURE.md`
- 脚本组织指南: 参见`scripts/README.md`



### 4. 版本管理

**分支策略**:

- `main`: 生产环境，仅接受 release 分支合并

- `develop`: 集成分支，功能测试通过后合并

- `feature/*`: 功能开发分支

- `hotfix/*`: 紧急修复分支

 

**提交规范**:

[类型] 简要描述 (关联ID)

详细说明（可选）

类型: FEATURE|BUGFIX|DOC|REFACTOR|TEST

text

 

---

 

## 三、测试与质量保障

 

### 1. 测试要求

**测试类型与覆盖范围**:

| 测试类型 | 核心目标 | 覆盖范围 | 执行频率 |

|---------|----------|----------|----------|

| 单元测试 | 验证单个函数/模块正确性 | 所有业务逻辑函数，覆盖率≥80% | 代码提交前 |

| 集成测试 | 验证模块间交互正确性 | 数据流转链路、接口兼容性 | 每日构建后 |

| 性能测试 | 验证系统性能达标 | 响应时间、吞吐量、资源占用 | 版本发布前 |

| 数据质量测试 | 验证数据准确性与完整性 | 完整性>99.9%、新鲜度<1秒延迟 | 每日执行 |

| 容错测试 | 验证异常处理能力 | 数据源中断、网络波动等场景 | 版本发布前 |

 

### 2. 测试用例规范

- 每个测试用例必须包含：场景描述、输入参数、预期结果、实际结果

- 历史 Bug 修复必须补充回归测试用例

- 测试用例按功能模块和 Bug ID 分类管理

 

### 3. 质量指标

**代码质量**:

- 语法错误：零容忍（flake8检查）

- 代码重复率：≤5%（radon检测）

- 函数复杂度：圈复杂度≤10

 

**数据质量**:

- 完整性：核心数据缺失率≤0.1%

- 准确性：数据值偏差≤0.01%

- 一致性：跨模块数据完全一致

 

**性能指标**:

- Redis热数据访问：P95响应时间<10ms

- TDengine高频查询：10万条Tick数据查询<100ms

- PostgreSQL复杂分析：1年日线数据统计<5s

- 数据采集吞吐量：支持1000+资产并发采集

 

### 4. 自动化测试流程

```yaml

# CI/CD流水线示例

stages:

  - 代码检查:

      - 语法检查 (pylint, flake8)

      - 类型检查 (mypy)

      - 安全扫描

  - 单元测试:

      - 核心功能测试

      - 边界条件测试

      - 回归测试套件

  - 集成测试:

      - 数据流验证

      - 接口兼容性测试

  - 性能测试:

      - 基准性能验证

      - 压力测试

四、代码修改规范

1. 核心原则

最小变更原则: 只修改目标相关的最小代码块，避免"顺带优化"
分层验证原则: 多层级验证确保修改质量
可回溯原则: 任何修改都必须能够快速回滚
透明化原则: 所有修改过程、Bug根因、修复方案需可追踪
架构合规原则: 100%遵循配置驱动架构，严禁临时补救
知识沉淀原则: 所有Bug修复案例需纳入知识库

2. 变更前置约束

保护范围定义 (PROTECTED.md):

markdown

# 禁止AI自动修改的核心模块

## 核心交易模块

1. `/core/trade_executor.py` - 交易执行核心

2. `/core/risk_manager.py` - 风险控制核心

3. `/core/position_manager.py` - 仓位管理核心

 

## 数据库相关

4. `/db/schema/` - 数据库表结构定义

5. `/db/migrations/` - 数据库迁移脚本

 

## 配置与参数

6. `/config/risk_limits.yaml` - 风险控制参数

7. `/config/trading_params.yaml` - 交易参数配置

保护范围检查:

每次修改前必须检查是否涉及保护范围
涉及保护范围的修改自动终止，需人工确认
提供修改建议而非直接修改
3. 分层验证机制

第一层：AI自验证

plaintext

=== AI 自查报告 ===

修改时间：2025-10-25 14:30

修改文件：/data_crawl/scripts/cleaner.py

修改类型：bug修复（关联 bug#006）

 

检查结果：

1. 语法检查：✅ 通过

2. 依赖检查：✅ 通过 

3. 业务规则：✅ 通过

4. 核心测试：✅ 通过

5. Bug排查：✅ 通过

 

风险评估：低风险

建议：可以进入下一层验证

第二层：自动化测试

yaml

测试金字塔：

  E2E测试 (10%)：历史Bug场景端到端验证

    ┌─────────────┐

    │集成测试 (20%)│：模块间交互Bug点覆盖

 ┌─────────────────┐

  │  单元测试 (70%)  │：每个Bug修复后的回归用例

 └─────────────────┘

第三层：人工审核
审核触发条件:

涉及保护范围的核心模块
变更影响范围超过单个函数
自动化测试出现新增失败用例
性能下降超过10%
修改模块的历史Bug次数≥3次
4. 变更申请流程

变更申请单模板:

markdown

## 变更申请单

**申请时间**：2025-10-25

**申请人**：AI Assistant 

**审核人**：JohnC

**关联Bug ID**：bug#006

 

### 变更内容

修复数据缺失值处理逻辑

 

### 修改文件

- `/data_crawl/scripts/cleaner.py`

- `/tests/test_cleaner.py`

 

### 关联测试

- 新增：`test_clean_missing_value()`

- 修复：3个回归测试用例

- 覆盖率：从75%提升到85%

 

### 潜在风险

可能影响依赖该函数的均线计算模块

 

### 回滚方案

- 保留原函数作为`clean_data_v1()`

- 提供快速回滚脚本

- 数据库变更提供回滚迁移

 

### 审核意见

- [ ] 同意修改

- [ ] 需要调整

- [ ] 拒绝修改

5. 架构合规检查

配置驱动验证:

✅ 所有表结构在配置文件中定义
✅ 通过配置管理器进行表创建
✅ 无独立SQL脚本绕过架构
✅ 无临时补救措施违背原则
禁止的临时补救案例:

python

# ❌ 错误做法：绕过配置驱动架构

# 直接执行SQL创建表，导致架构不一致

 

# ✅ 正确做法：通过配置管理器

ConfigDrivenTableManager.batch_create_tables(table_configs)

6. Bug管理体系

Bug记录模板:

markdown

## Bug记录：bug#006

**发现时间**：2025-10-25

**影响模块**：数据清洗模块

**根本原因**：缺失值边界判断缺失

**修复方案**：新增边界值检查逻辑

**回归测试**：test_clean_missing_value()

**知识沉淀**：同类数据处理需注意边界条件

Bug统计分析:

按模块统计Bug发生频率
按类型统计Bug分布
按严重程度统计影响范围
定期输出质量改进报告
五、治理与修订

1. 宪法权威性

本宪法是项目开发的最高指导规范
所有代码、文档、架构决策必须符合宪法要求
若存在冲突，以本宪法为准
2. 修订流程

修订步骤:

提交修订提案: 包含修订理由、内容、影响分析
团队评审: 核心团队（开发、测试、业务）评审
试点验证: 在试点环境验证，确认无破坏性影响
请示批准: 提交请求，待负责人JohnC批准
版本更新: 更新宪法版本号，记录修订日志
3. 合规审查

所有代码提交必须包含"合规性自查报告"
每季度开展宪法合规审计
输出审计报告并整改问题
建立持续改进机制
4. 度量与改进

关键度量指标:

部署频率、变更前置时间
变更失败率、平均恢复时间
代码质量评分、技术债务比率
Bug复发率、测试覆盖率
改进机制:

基于度量的持续优化
定期回顾和流程改进
知识分享和经验沉淀
技术债务管理和偿还
附件

1. 术语表

配置驱动: 通过外部配置控制系统行为的设计模式
数据分类: 基于特征对数据进行分类管理的方法
可观测性: 通过日志、指标、追踪理解系统状态的能力
圈复杂度: 衡量代码复杂度的指标
语义化版本: 版本号管理规范
2. 参考标准

语义化版本 (SemVer 2.0.0)
PEP 8 Python代码风格指南
十二要素应用方法论
ISO 25010 软件质量模型
本文档是项目开发的最高指导原则，所有参与者必须熟悉并遵守。修订时需确保内容的完整性和一致性。如有疑问或改进建议，请通过修订流程提出。