"""
T0XX: Pre-commit配置验证单元测试

验证.pre-commit-config.yaml配置文件的完整性和正确性,
包括仓库定义、钩子配置、版本和排除规则等。

创建日期: 2025-12-23
版本: 1.0.0
"""

import os
import yaml
import pytest

class TestPreCommitConfig:
    """Pre-commit配置验证测试类"""

    @classmethod
    def setup_class(cls):
        """测试类初始化：读取并解析.pre-commit-config.yaml文件"""
        cls.pre_commit_config_path = ".pre-commit-config.yaml"
        assert os.path.exists(cls.pre_commit_config_path), \
            f"Pre-commit配置文件不存在: {cls.pre_commit_config_path}"

        with open(cls.pre_commit_config_path, 'r', encoding='utf-8') as f:
            cls.config = yaml.safe_load(f)

    def test_01_repos_section_exists(self):
        """测试1: 验证配置中是否存在'repos'节且为列表"""
        print("📍 测试1: 验证配置中是否存在'repos'节且为列表")
        assert 'repos' in self.config, "缺少'repos'顶级键"
        assert isinstance(self.config['repos'], list), "'repos'键的值应该是一个列表"
        print("  ✅ 'repos'节验证通过")

    def test_02_ruff_repo_and_hooks(self):
        """测试2: 验证Ruff仓库及其钩子配置"""
        print("\n📍 测试2: 验证Ruff仓库及其钩子配置")
        ruff_repo = next((repo for repo in self.config['repos'] 
                          if repo.get('repo') == 'https://github.com/astral-sh/ruff-pre-commit'), None)
        
        assert ruff_repo is not None, "未找到'ruff-pre-commit'仓库配置"
        assert ruff_repo.get('rev') == 'v0.4.4', "Ruff仓库版本不正确"
        
        hooks = ruff_repo.get('hooks', [])
        assert any(hook.get('id') == 'ruff' for hook in hooks), "未找到'ruff'钩子"
        assert any(hook.get('id') == 'ruff-format' for hook in hooks), "未找到'ruff-format'钩子"
        
        # 验证ruff钩子的args
        ruff_hook = next((hook for hook in hooks if hook.get('id') == 'ruff'), None)
        assert ruff_hook is not None and ruff_hook.get('args') == ['--fix'], "'ruff'钩子参数不正确"
        
        print("  ✅ Ruff仓库及其钩子配置验证通过")

    def test_03_mypy_repo_and_hooks(self):
        """测试3: 验证MyPy仓库及其钩子配置"""
        print("\n📍 测试3: 验证MyPy仓库及其钩子配置")
        mypy_repo = next((repo for repo in self.config['repos'] 
                          if repo.get('repo') == 'https://github.com/pre-commit/mirrors-mypy'), None)
        
        assert mypy_repo is not None, "未找到'mirrors-mypy'仓库配置"
        assert mypy_repo.get('rev') == 'v1.10.0', "MyPy仓库版本不正确"
        
        hooks = mypy_repo.get('hooks', [])
        mypy_hook = next((hook for hook in hooks if hook.get('id') == 'mypy'), None)
        assert mypy_hook is not None, "未找到'mypy'钩子"
        
        expected_args = ['--ignore-missing-imports', '--no-error-summary']
        assert mypy_hook.get('args') == expected_args, "'mypy'钩子参数不正确"
        assert 'exclude' in mypy_hook and mypy_hook['exclude'], "'mypy'钩子缺少排除规则"
        
        print("  ✅ MyPy仓库及其钩子配置验证通过")

    def test_04_bandit_repo_and_hooks(self):
        """测试4: 验证Bandit仓库及其钩子配置"""
        print("\n📍 测试4: 验证Bandit仓库及其钩子配置")
        bandit_repo = next((repo for repo in self.config['repos'] 
                            if repo.get('repo') == 'https://github.com/PyCQA/bandit'), None)
        
        assert bandit_repo is not None, "未找到'bandit'仓库配置"
        assert bandit_repo.get('rev') == '1.7.8', "Bandit仓库版本不正确"
        
        hooks = bandit_repo.get('hooks', [])
        bandit_hook = next((hook for hook in hooks if hook.get('id') == 'bandit'), None)
        assert bandit_hook is not None, "未找到'bandit'钩子"
        
        expected_args = ['-c', 'config/.security.yml', '-ll']
        assert bandit_hook.get('args') == expected_args, "'bandit'钩子参数不正确"
        assert 'exclude' in bandit_hook and bandit_hook['exclude'], "'bandit'钩子缺少排除规则"
        
        print("  ✅ Bandit仓库及其钩子配置验证通过")

    def test_05_general_hooks_repo_and_hooks(self):
        """测试5: 验证通用钩子仓库及其钩子配置"""
        print("\n📍 测试5: 验证通用钩子仓库及其钩子配置")
        general_repo = next((repo for repo in self.config['repos'] 
                             if repo.get('repo') == 'https://github.com/pre-commit/pre-commit-hooks'), None)
        
        assert general_repo is not None, "未找到'pre-commit-hooks'仓库配置"
        assert general_repo.get('rev') == 'v4.6.0', "通用钩子仓库版本不正确"
        
        hooks = general_repo.get('hooks', [])
        expected_hooks_ids = ['trailing-whitespace', 'end-of-file-fixer', 'check-yaml', 'check-json', 
                              'check-added-large-files', 'detect-private-key', 'check-merge-conflict']
        
        for hook_id in expected_hooks_ids:
            assert any(hook.get('id') == hook_id for hook in hooks), f"未找到'{hook_id}'钩子"
        
        # 验证detect-private-key的exclude
        detect_private_key_hook = next((hook for hook in hooks if hook.get('id') == 'detect-private-key'), None)
        assert detect_private_key_hook is not None and 'exclude' in detect_private_key_hook and detect_private_key_hook['exclude'], \
            "'detect-private-key'钩子缺少排除规则"
        
        print("  ✅ 通用钩子仓库及其钩子配置验证通过")

    def test_06_detect_secrets_repo_and_hooks(self):
        """测试6: 验证Detect Secrets仓库及其钩子配置"""
        print("\n📍 测试6: 验证Detect Secrets仓库及其钩子配置")
        detect_secrets_repo = next((repo for repo in self.config['repos'] 
                                   if repo.get('repo') == 'https://github.com/Yelp/detect-secrets'), None)
        
        assert detect_secrets_repo is not None, "未找到'detect-secrets'仓库配置"
        assert detect_secrets_repo.get('rev') == 'v1.5.0', "Detect Secrets仓库版本不正确"
        
        hooks = detect_secrets_repo.get('hooks', [])
        detect_secrets_hook = next((hook for hook in hooks if hook.get('id') == 'detect-secrets'), None)
        assert detect_secrets_hook is not None, "未找到'detect-secrets'钩子"
        assert 'exclude' in detect_secrets_hook and detect_secrets_hook['exclude'], "'detect-secrets'钩子缺少排除规则"
        
        print("  ✅ Detect Secrets仓库及其钩子配置验证通过")

    def test_07_pygrep_hooks_repo_and_hooks(self):
        """测试7: 验证Pygrep Hooks仓库及其钩子配置"""
        print("\n📍 测试7: 验证Pygrep Hooks仓库及其钩子配置")
        pygrep_repo = next((repo for repo in self.config['repos'] 
                            if repo.get('repo') == 'https://github.com/pre-commit/pygrep-hooks'), None)
        
        assert pygrep_repo is not None, "未找到'pygrep-hooks'仓库配置"
        assert pygrep_repo.get('rev') == 'v1.10.0', "Pygrep Hooks仓库版本不正确"
        
        hooks = pygrep_repo.get('hooks', [])
        expected_hooks_ids = ['python-check-blanket-noqa', 'python-check-blanket-type-ignore', 
                              'python-no-eval', 'python-no-log-warn']
        
        for hook_id in expected_hooks_ids:
            assert any(hook.get('id') == hook_id for hook in hooks), f"未找到'{hook_id}'钩子"
        
        print("  ✅ Pygrep Hooks仓库及其钩子配置验证通过")

# if __name__ == "__main__":
#     pytest.main([__file__])
