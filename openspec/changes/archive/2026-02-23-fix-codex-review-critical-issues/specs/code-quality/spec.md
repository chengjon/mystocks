# Code Quality Spec Delta

## MODIFIED Requirements

### Requirement: Python Class Structure Integrity
所有 Python 类定义 MUST 保持正确的缩进结构，确保类方法正确定义在类作用域内。

#### Scenario: Class method indentation
- **WHEN** 定义 Python 类时
- **THEN** 所有类方法 SHALL 缩进到类定义内部
- **AND** MUST 使用一致的缩进层级（4个空格）

#### Scenario: Class structure validation
- **WHEN** 进行代码审查或质量检查
- **THEN** 开发者 MUST 使用 AST 解析验证类结构
- **AND** MUST 确认 `__init__` 和其他核心方法在类内部

### Requirement: Documentation Link Validity
项目文档（特别是 README.md）中的所有本地链接 MUST 指向存在的文件。

#### Scenario: Link verification
- **WHEN** 创建或更新文档链接
- **THEN** 链接目标文件 MUST 存在
- **AND** 链接路径 SHALL 相对于项目根目录正确

#### Scenario: Link validation tools
- **WHEN** 维护文档
- **THEN** 开发者 SHALL 提供自动化工具验证链接有效性
- **AND** 工具 MUST 返回正确的退出码（0=成功，1=失败）

### Requirement: GPU Documentation Path Accuracy
所有 GPU 相关文档引用 MUST 使用正确的路径 `src/gpu/api_system/`。

#### Scenario: GPU path references
- **WHEN** 引用 GPU 系统文档
- **THEN** 开发者 MUST 使用路径 `src/gpu/api_system/`
- **AND** MUST NOT 使用过时的 `gpu_api_system/` 路径

### Requirement: Code Review Response Protocol
当收到代码审查报告时，开发团队 MUST 按照严格流程进行修复和验证。

#### Scenario: Critical issue resolution
- **WHEN** Codex 审查发现 Critical 问题
- **THEN** 开发者 MUST 立即修复并验证
- **AND** MUST 使用可执行的验证脚本确认修复有效

#### Scenario: Validation scripts
- **WHEN** 创建验证脚本
- **THEN** 脚本 MUST 使用 `set -e` 确保失败时退出
- **AND** MUST NOT 使用 `|| echo` 吞掉错误
- **AND** MUST 返回正确的退出码

## REMOVED Requirements

无

## RENAMED Requirements

无
