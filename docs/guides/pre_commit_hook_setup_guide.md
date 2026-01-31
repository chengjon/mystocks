# Pre-commit Hook - 文件大小检查配置

**项目**: MyStocks 代码重构
**目标**: 阻止 > 500行的新文件提交
**优先级**: P0 (高优先级）

---

## 📋 Hook配置

### 1. 文件大小检查 Hook

**目的**: 检查所有新增或修改的文件，确保 < 500行
**例外**: 配置文件、README、文档文件等可豁免

**Hook配置文件**: `.pre-commit-config.yaml`

```yaml
# 文件大小检查
repos:
  - repo: .
    hooks:
      - id: check-file-size
        name: Check file size
        entry: scripts/check_file_size.py
        language: system
        types: [python]
        pass_filenames: true  # 只检查文件名
        exclude: ^(.*\.md$|.*\.txt$|.*\.yaml$|.*\.yml$|.*\.json$|.*\.git.*|.*\.env.*)  # 排除文档和配置
```

### 2. Python脚本：scripts/check_file_size.py

**位置**: `scripts/check_file_size.py`
**功能**: 检查文件行数，> 500行返回失败

```python
#!/usr/bin/env python3
"""
文件大小检查脚本
检查所有新增/修改的文件，确保 < 500行
"""

import sys
import os
from pathlib import Path

# 可豁免的文件扩展名
WHITELIST = ['.md', '.txt', '.yaml', '.yml', '.json', '.git', '.env', '.toml', '.ini']

# 可豁免的目录
WHITELIST_DIRS = [
    'node_modules',
    '.git',
    '__pycache__',
    'venv',
    'env',
    '.vscode',
    'dist',
    'build'
]

# 行数限制
MAX_LINES = 500

def is_whitelisted(file_path):
    """检查文件是否在白名单中"""
    return any(file_path.suffix.lower() in WHITELIST)

def is_in_whitelisted_dir(file_path):
    """检查文件是否在白名单目录中"""
    return any(part in file_path.parts for part in WHITELIST_DIRS)

def check_file_size(file_path, added_files, modified_files):
    """检查单个文件"""
    # 转换为Path对象
    path = Path(file_path)

    # 跳过白名单文件
    if is_whitelisted(path):
        return True

    # 跳过白名单目录中的文件
    if is_in_whitelisted_dir(path):
        return True

    # 只检查新增或修改的文件
    if str(path) not in added_files and str(path) not in modified_files:
        return True

    # 检查Python/Vue文件
    if path.suffix.lower() in ['.py', '.vue']:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                line_count = sum(1 for _ in f)

            if line_count > MAX_LINES:
                print(f"❌ {path}: {line_count} 行 (超过 {MAX_LINES} 行限制)")
                print(f"💡 建议: 将此文件拆分为多个小文件")
                return False
            else:
                return True
        except Exception as e:
            print(f"⚠️ 无法读取 {path}: {e}")
            return True

    return True

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("❌ 用法: python3 check_file_size.py <added_files> <modified_files>")
        print("   <added_files>: 新增文件列表（空格分隔）")
        print("   <modified_files>: 修改文件列表（空格分隔）")
        sys.exit(1)

    # 获取文件列表
    added_files = sys.argv[1].split() if sys.argv[1] else []
    modified_files = sys.argv[2].split() if len(sys.argv) > 2 else []

    # 获取当前目录
    files_to_check = []
    if added_files or modified_files:
        for file_list in [added_files, modified_files]:
            files_to_check.extend(file_list)

    # 检查所有文件
    all_passed = True
    for file_path_str in files_to_check:
        file_path = Path(file_path_str)
        if file_path.is_file():
            passed = check_file_size(file_path, added_files, modified_files)
            if not passed:
                all_passed = False

    # 返回结果
    if not all_passed:
        print("\n❌ 文件大小检查失败！")
        print(f"💡 请确保所有Python/Vue文件 < {MAX_LINES} 行")
        sys.exit(1)
    else:
        print(f"✅ 所有文件检查通过 (< {MAX_LINES} 行)")
        sys.exit(0)

if __name__ == "__main__":
    main()
```

### 3. 安装步骤

```bash
# 1. 创建scripts目录
mkdir -p scripts

# 2. 创建check_file_size.py脚本
# (将上面的Python代码保存到scripts/check_file_size.py）

# 3. 安装pre-commit
pip install pre-commit

# 4. 安装配置
pre-commit install

# 5. 验证安装
pre-commit run --all-files
```

### 4. 测试Hook

```bash
# 创建测试文件
echo "# test file
" > test_large_file.py; for i in {1..501}; do echo "print('$i')" >> test_large_file.py; done

# 运行检查脚本
python3 scripts/check_file_size.py test_large_file.py
# 应该失败（501行）

# 测试正常文件
echo "# test file
" > test_small_file.py; for i in {1..400}; do echo "print('$i')" >> test_small_file.py; done

# 运行检查脚本
python3 scripts/check_file_size.py test_small_file.py
# 应该成功（400行）
```

---

## 📋 验收标准

- [ ] Pre-commit已安装
- [ ] .pre-commit-config.yaml已配置
- [ ] check_file_size.py脚本已创建
- [ ] Hook可正常工作（测试> 500行文件被拒绝）
- [ ] Hook允许< 500行文件
- [ ] 文档文件（.md, .yaml等）被豁免

---

## 📊 成功指标

- **拦截率**: 100%（所有> 500行文件被拦截）
- **误报率**: < 5%（正常文件偶尔被误报）
- **响应时间**: < 2秒（每个文件检查）
- **开发体验**: 开发者明确看到失败原因

---

## 🚀 部署步骤

### 1. 创建文件结构

```bash
cd mystocks_spec
mkdir -p scripts
```

### 2. 创建脚本文件

```bash
# 创建scripts/check_file_size.py
# (将上面的Python代码保存)
```

### 3. 创建配置文件

```bash
# 创建.pre-commit-config.yaml
# (将上面的YAML配置保存）
```

### 4. 安装和配置

```bash
# 安装pre-commit
pip install pre-commit

# 安装配置
pre-commit install

# 验证安装
pre-commit run --all-files
```

---

## 📝 配置说明

### 豁免列表

**文件类型**:
- Markdown文件 (.md)
- 文本文件 (.txt)
- YAML文件 (.yaml, .yml)
- JSON文件 (.json)
- 配置文件 (.toml, .ini)
- Git相关 (.gitignore, .gitattributes)

**目录**:
- node_modules/
- .git/
- __pycache__/
- venv/
- env/
- .vscode/
- dist/
- build/

### 检查规则

1. **只检查代码文件**: Python (.py) 和 Vue (.vue)
2. **行数限制**: 500行（硬编码）
3. **错误提示**: 显示实际行数和建议
4. **退出码**: 失败时返回1，成功时返回0

---

## 📋 故障排查

### Hook未触发

1. **检查配置文件位置**: 应在项目根目录
2. **检查安装状态**: 运行 `pre-commit --version`
3. **检查hooks**: 运行 `pre-commit --all-hooks`

### Hook触发但失败

1. **检查Python路径**: 确保脚本可执行权限
2. **检查依赖**: 确保安装了所有需要的包
3. **检查日志**: 运行 `pre-commit run --verbose`

### 误报

1. **检查白名单**: 确认文件类型和目录在白名单中
2. **检查文件编码**: 确保使用UTF-8编码

---

## 📋 使用指南

### 日常开发

1. **正常提交**: 使用 `git commit`，hook会自动检查
2. **跳过检查**: 如需提交大文件，使用 `git commit --no-verify`
3. **手动检查**: 运行 `pre-commit run --files <file1> <file2>`

### 团队协作

1. **共享配置**: 将.pre-commit-config.yaml提交到仓库
2. **统一标准**: 确保所有团队成员使用相同的配置
3. **文档**: 更新开发规范文档，说明< 500行要求

---

## 📋 注意事项

1. **兼容性**: Hook脚本需要在所有开发环境中安装
2. **性能**: Hook应该快速，不影响开发体验
3. **维护**: 白名单需要根据项目需求定期更新
4. **培训**: 团队成员需要培训，理解Hook的作用和失败原因

---

**创建时间**: 2026-01-30T09:00:00Z
**执行人**: Claude Code
**版本**: v1.0
**状态**: 准备部署

---

## 🎯 下一步行动

1. **立即执行**: 创建scripts/check_file_size.py和.pre-commit-config.yaml
2. **测试验证**: 测试Hook功能和性能
3. **文档更新**: 更新开发规范文档
4. **团队通知**: 通知团队成员新的开发流程
