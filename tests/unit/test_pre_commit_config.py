"""
T0XX: Pre-commit配置验证单元测试

验证.pre-commit-config.yaml配置文件的完整性和正确性,
包括仓库定义、钩子配置、版本和排除规则等。

创建日期: 2025-12-23
版本: 1.0.0
"""

import os
import re

import yaml


VERSION_PATTERN = re.compile(r"^v?\d+\.\d+\.\d+(?:[-+._][A-Za-z0-9]+)*$")


def assert_pinned_revision(revision: str | None) -> None:
    assert revision is not None and revision.strip(), "仓库版本不能为空"
    assert revision not in {"main", "master", "HEAD", "latest"}, "仓库版本必须固定，不能使用浮动引用"
    assert VERSION_PATTERN.match(revision), f"仓库版本格式异常: {revision}"


class TestPreCommitConfig:
    """Pre-commit配置验证测试类"""

    @classmethod
    def setup_class(cls):
        """测试类初始化：读取并解析.pre-commit-config.yaml文件"""
        cls.pre_commit_config_path = ".pre-commit-config.yaml"
        assert os.path.exists(cls.pre_commit_config_path), f"Pre-commit配置文件不存在: {cls.pre_commit_config_path}"

        with open(cls.pre_commit_config_path, "r", encoding="utf-8") as f:
            cls.config = yaml.safe_load(f)

    def _find_repos(self, repo_url: str) -> list[dict]:
        return [repo for repo in self.config["repos"] if repo.get("repo") == repo_url]

    def test_01_repos_section_exists(self):
        """测试1: 验证配置中是否存在'repos'节且为列表"""
        print("📍 测试1: 验证配置中是否存在'repos'节且为列表")
        assert "repos" in self.config, "缺少'repos'顶级键"
        assert isinstance(self.config["repos"], list), "'repos'键的值应该是一个列表"
        print("  ✅ 'repos'节验证通过")

    def test_02_ruff_repo_and_hooks(self):
        """测试2: 验证Ruff仓库及其钩子配置"""
        print("\n📍 测试2: 验证Ruff仓库及其钩子配置")
        ruff_repos = self._find_repos("https://github.com/astral-sh/ruff-pre-commit")

        assert len(ruff_repos) == 2, "Ruff仓库应拆分为选择性修复和最终检查两个条目"
        revisions = {repo.get("rev") for repo in ruff_repos}
        assert len(revisions) == 1, "两个Ruff仓库条目应保持同一固定版本"
        assert_pinned_revision(next(iter(revisions)))

        all_hooks = [hook for repo in ruff_repos for hook in repo.get("hooks", [])]
        ruff_hooks = [hook for hook in all_hooks if hook.get("id") == "ruff"]
        assert len(ruff_hooks) == 2, "应存在两个ruff钩子（Selective Fix / Final Check）"

        selective_fix_hook = next((hook for hook in ruff_hooks if hook.get("name") == "Ruff (Selective Fix)"), None)
        assert selective_fix_hook is not None, "未找到Ruff选择性修复钩子"
        assert selective_fix_hook.get("args") == ["--select", "F401", "F841", "--fix"], "Ruff选择性修复参数不正确"

        final_check_hook = next((hook for hook in ruff_hooks if hook.get("name") == "Ruff (Final Check)"), None)
        assert final_check_hook is not None, "未找到Ruff最终检查钩子"
        assert final_check_hook.get("args") == ["--no-fix"], "Ruff最终检查参数不正确"

        print("  ✅ Ruff仓库及其钩子配置验证通过")

    def test_03_mypy_repo_and_hooks(self):
        """测试3: 验证MyPy仓库及其钩子配置"""
        print("\n📍 测试3: 验证MyPy仓库及其钩子配置")
        mypy_repo = next(
            (repo for repo in self.config["repos"] if repo.get("repo") == "https://github.com/pre-commit/mirrors-mypy"),
            None,
        )

        assert mypy_repo is not None, "未找到'mirrors-mypy'仓库配置"
        assert_pinned_revision(mypy_repo.get("rev"))

        hooks = mypy_repo.get("hooks", [])
        mypy_hook = next((hook for hook in hooks if hook.get("id") == "mypy"), None)
        assert mypy_hook is not None, "未找到'mypy'钩子"

        expected_args = ["--ignore-missing-imports", "--no-error-summary"]
        assert mypy_hook.get("args") == expected_args, "'mypy'钩子参数不正确"
        assert (
            ("exclude" in mypy_hook and mypy_hook["exclude"]) or ("files" in mypy_hook and mypy_hook["files"])
        ), "'mypy'钩子缺少作用范围约束"

        print("  ✅ MyPy仓库及其钩子配置验证通过")

    def test_04_bandit_repo_and_hooks(self):
        """测试4: 验证Bandit仓库及其钩子配置"""
        print("\n📍 测试4: 验证Bandit仓库及其钩子配置")
        bandit_repo = next(
            (repo for repo in self.config["repos"] if repo.get("repo") == "https://github.com/PyCQA/bandit"),
            None,
        )

        assert bandit_repo is not None, "未找到'bandit'仓库配置"
        assert_pinned_revision(bandit_repo.get("rev"))

        hooks = bandit_repo.get("hooks", [])
        bandit_hook = next((hook for hook in hooks if hook.get("id") == "bandit"), None)
        assert bandit_hook is not None, "未找到'bandit'钩子"

        expected_args = ["-c", "config/.security.yml", "-ll"]
        assert bandit_hook.get("args") == expected_args, "'bandit'钩子参数不正确"
        assert "exclude" in bandit_hook and bandit_hook["exclude"], "'bandit'钩子缺少排除规则"

        print("  ✅ Bandit仓库及其钩子配置验证通过")

    def test_05_general_hooks_repo_and_hooks(self):
        """测试5: 验证通用钩子仓库及其钩子配置"""
        print("\n📍 测试5: 验证通用钩子仓库及其钩子配置")
        general_repo = next(
            (
                repo
                for repo in self.config["repos"]
                if repo.get("repo") == "https://github.com/pre-commit/pre-commit-hooks"
            ),
            None,
        )

        assert general_repo is not None, "未找到'pre-commit-hooks'仓库配置"
        assert_pinned_revision(general_repo.get("rev"))

        hooks = general_repo.get("hooks", [])
        expected_hooks_ids = [
            "trailing-whitespace",
            "end-of-file-fixer",
            "check-yaml",
            "check-json",
            "check-added-large-files",
            "detect-private-key",
            "check-merge-conflict",
        ]

        for hook_id in expected_hooks_ids:
            assert any(hook.get("id") == hook_id for hook in hooks), f"未找到'{hook_id}'钩子"

        # 验证detect-private-key的exclude
        detect_private_key_hook = next((hook for hook in hooks if hook.get("id") == "detect-private-key"), None)
        assert (
            detect_private_key_hook is not None
            and "exclude" in detect_private_key_hook
            and detect_private_key_hook["exclude"]
        ), "'detect-private-key'钩子缺少排除规则"

        print("  ✅ 通用钩子仓库及其钩子配置验证通过")

    def test_06_detect_secrets_repo_and_hooks(self):
        """测试6: 验证Detect Secrets仓库及其钩子配置"""
        print("\n📍 测试6: 验证Detect Secrets仓库及其钩子配置")
        detect_secrets_repo = next(
            (repo for repo in self.config["repos"] if repo.get("repo") == "https://github.com/Yelp/detect-secrets"),
            None,
        )

        assert detect_secrets_repo is not None, "未找到'detect-secrets'仓库配置"
        assert_pinned_revision(detect_secrets_repo.get("rev"))

        hooks = detect_secrets_repo.get("hooks", [])
        detect_secrets_hook = next((hook for hook in hooks if hook.get("id") == "detect-secrets"), None)
        assert detect_secrets_hook is not None, "未找到'detect-secrets'钩子"
        assert "exclude" in detect_secrets_hook and detect_secrets_hook["exclude"], "'detect-secrets'钩子缺少排除规则"

        print("  ✅ Detect Secrets仓库及其钩子配置验证通过")

    def test_07_pygrep_hooks_repo_and_hooks(self):
        """测试7: 验证Pygrep Hooks仓库及其钩子配置"""
        print("\n📍 测试7: 验证Pygrep Hooks仓库及其钩子配置")
        pygrep_repo = next(
            (repo for repo in self.config["repos"] if repo.get("repo") == "https://github.com/pre-commit/pygrep-hooks"),
            None,
        )

        assert pygrep_repo is not None, "未找到'pygrep-hooks'仓库配置"
        assert_pinned_revision(pygrep_repo.get("rev"))

        hooks = pygrep_repo.get("hooks", [])
        expected_hooks_ids = [
            "python-check-blanket-noqa",
            "python-check-blanket-type-ignore",
            "python-no-eval",
            "python-no-log-warn",
        ]

        for hook_id in expected_hooks_ids:
            assert any(hook.get("id") == hook_id for hook in hooks), f"未找到'{hook_id}'钩子"

        print("  ✅ Pygrep Hooks仓库及其钩子配置验证通过")

    def test_08_page_config_validator_local_hook(self):
        """测试8: 验证前端页面配置校验钩子存在且结构正确"""
        print("\n📍 测试8: 验证前端页面配置校验钩子")
        local_repos = self._find_repos("local")
        page_config_hook = None

        for repo in local_repos:
            for hook in repo.get("hooks", []):
                if hook.get("id") == "page-config-validator":
                    page_config_hook = hook
                    break
            if page_config_hook is not None:
                break

        assert page_config_hook is not None, "未找到'page-config-validator'本地钩子"
        assert page_config_hook.get("name") == "Page Configuration Validator", "page-config-validator 名称不正确"
        assert page_config_hook.get("language") == "system", "page-config-validator 语言类型不正确"
        assert page_config_hook.get("files") == r"^web/frontend/src/(router/|config/)", "page-config-validator 文件范围不正确"
        assert page_config_hook.get("pass_filenames") is False, "page-config-validator 不应接收文件名参数"
        assert page_config_hook.get("always_run") is True, "page-config-validator 应保持 always_run"
        assert page_config_hook.get("stages") == ["pre-commit"], "page-config-validator stages 不正确"
        assert "check-page-config.mjs --warn || true" in page_config_hook.get("entry", ""), "page-config-validator entry 不正确"

        print("  ✅ page-config-validator 钩子配置验证通过")

    def test_09_frontend_local_hooks_are_grouped(self):
        """测试9: 验证前端质量相关本地钩子按同一分组组织"""
        print("\n📍 测试9: 验证前端本地钩子分组")
        local_repos = self._find_repos("local")

        frontend_group_found = False
        for repo in local_repos:
            hook_ids = {hook.get("id") for hook in repo.get("hooks", [])}
            if {"typescript-check", "page-config-validator", "artdeco-token-lint"}.issubset(hook_ids):
                frontend_group_found = True
                break

        assert frontend_group_found, "typescript-check、page-config-validator、artdeco-token-lint 应放在同一个 local repo 分组中"

        print("  ✅ 前端本地钩子分组验证通过")

    def test_10_section_titles_use_consistent_naming(self):
        """测试10: 验证 pre-commit 章节标题采用统一命名风格"""
        print("\n📍 测试10: 验证章节标题命名风格")
        content = open(self.pre_commit_config_path, "r", encoding="utf-8").read()

        expected_titles = [
            "# 第一步：Black 格式化",
            "# 第二步：Ruff 选择性修复",
            "# 第三步：Ruff 最终检查",
            "# 第十步：文档治理与主线提醒",
            "# 第十一步：目录结构与生产 Python 门禁",
            "# 第十三步：硬编码与迁移门禁",
        ]

        for title in expected_titles:
            assert title in content, f"缺少统一后的章节标题: {title}"

        print("  ✅ 章节标题命名风格验证通过")

    def test_11_top_level_comments_use_compact_maintainer_note(self):
        """测试11: 验证顶部说明已压缩为维护者摘要"""
        print("\n📍 测试11: 验证顶部维护说明")
        content = open(self.pre_commit_config_path, "r", encoding="utf-8").read()

        expected_lines = [
            "# Pre-commit configuration for MyStocks project",
            "# Install: pip install pre-commit && pre-commit install",
            "# Run manually: pre-commit run --all-files",
            "# 维护要点：Black 负责格式化，Ruff 负责 lint，local hooks 负责治理门禁",
            "# 执行顺序：Black → Ruff selective fix → Ruff final check → MyPy → Bandit → Safety",
        ]

        for line in expected_lines:
            assert line in content, f"缺少顶部维护说明: {line}"

        assert "# 关键避坑点：" not in content, "顶部说明仍然保留了冗长的旧段落"

        print("  ✅ 顶部维护说明验证通过")

    def test_12_artdeco_token_lint_local_hook(self):
        """测试12: 验证 ArtDeco token lint 已接入本地钩子"""
        print("\n📍 测试12: 验证 ArtDeco token lint 本地钩子")
        local_repos = self._find_repos("local")
        artdeco_hook = None

        for repo in local_repos:
            for hook in repo.get("hooks", []):
                if hook.get("id") == "artdeco-token-lint":
                    artdeco_hook = hook
                    break
            if artdeco_hook is not None:
                break

        assert artdeco_hook is not None, "未找到'artdeco-token-lint'本地钩子"
        assert artdeco_hook.get("name") == "ArtDeco Token Lint", "artdeco-token-lint 名称不正确"
        assert artdeco_hook.get("language") == "system", "artdeco-token-lint 语言类型不正确"
        assert artdeco_hook.get("files") == r"^web/frontend/src/.*\.(vue|scss|css)$", "artdeco-token-lint 文件范围不正确"
        assert artdeco_hook.get("pass_filenames") is False, "artdeco-token-lint 不应接收文件名参数"
        assert artdeco_hook.get("stages") == ["pre-commit"], "artdeco-token-lint stages 不正确"
        assert "npm run lint:artdeco" in artdeco_hook.get("entry", ""), "artdeco-token-lint entry 不正确"

        print("  ✅ ArtDeco token lint 本地钩子验证通过")

    def test_13_observability_readiness_gate_local_hook(self):
        """测试13: 验证 Observability readiness gate 已接入本地钩子"""
        print("\n📍 测试13: 验证 Observability readiness gate 本地钩子")
        local_repos = self._find_repos("local")
        readiness_hook = None

        for repo in local_repos:
            for hook in repo.get("hooks", []):
                if hook.get("id") == "observability-readiness-gate":
                    readiness_hook = hook
                    break
            if readiness_hook is not None:
                break

        assert readiness_hook is not None, "未找到'observability-readiness-gate'本地钩子"
        assert readiness_hook.get("name") == "Observability Readiness Gate", "observability-readiness-gate 名称不正确"
        assert readiness_hook.get("language") == "system", "observability-readiness-gate 语言类型不正确"
        assert readiness_hook.get("pass_filenames") is False, "observability-readiness-gate 不应接收文件名参数"
        assert readiness_hook.get("always_run") is True, "observability-readiness-gate 应保持 always_run"
        assert readiness_hook.get("stages") == ["pre-commit"], "observability-readiness-gate stages 不正确"
        assert "python scripts/compliance/readiness_contract_gate.py --format text" in readiness_hook.get(
            "entry", ""
        ), "observability-readiness-gate entry 不正确"

        print("  ✅ Observability readiness gate 本地钩子验证通过")

    def test_14_app_route_purity_gate_local_hook(self):
        """测试14: 验证 App route purity gate 已接入本地钩子"""
        print("\n📍 测试14: 验证 App route purity gate 本地钩子")
        local_repos = self._find_repos("local")
        purity_hook = None

        for repo in local_repos:
            for hook in repo.get("hooks", []):
                if hook.get("id") == "app-route-purity-gate":
                    purity_hook = hook
                    break
            if purity_hook is not None:
                break

        assert purity_hook is not None, "未找到'app-route-purity-gate'本地钩子"
        assert purity_hook.get("name") == "App Route Purity Gate", "app-route-purity-gate 名称不正确"
        assert purity_hook.get("language") == "system", "app-route-purity-gate 语言类型不正确"
        assert purity_hook.get("pass_filenames") is False, "app-route-purity-gate 不应接收文件名参数"
        assert purity_hook.get("always_run") is True, "app-route-purity-gate 应保持 always_run"
        assert purity_hook.get("stages") == ["pre-commit"], "app-route-purity-gate stages 不正确"
        assert "python scripts/compliance/app_route_purity_gate.py --format text" in purity_hook.get(
            "entry", ""
        ), "app-route-purity-gate entry 不正确"

        print("  ✅ App route purity gate 本地钩子验证通过")

    def test_15_request_id_visibility_gate_local_hook(self):
        """测试15: 验证 Request ID visibility gate 已接入本地钩子"""
        print("\n📍 测试15: 验证 Request ID visibility gate 本地钩子")
        local_repos = self._find_repos("local")
        visibility_hook = None

        for repo in local_repos:
            for hook in repo.get("hooks", []):
                if hook.get("id") == "request-id-visibility-gate":
                    visibility_hook = hook
                    break
            if visibility_hook is not None:
                break

        assert visibility_hook is not None, "未找到'request-id-visibility-gate'本地钩子"
        assert visibility_hook.get("name") == "Request ID Visibility Gate", "request-id-visibility-gate 名称不正确"
        assert visibility_hook.get("language") == "system", "request-id-visibility-gate 语言类型不正确"
        assert visibility_hook.get("files") == r"^web/frontend/src/views/artdeco-pages/[^/]+-tabs/[^/]+\.vue$", (
            "request-id-visibility-gate 文件范围不正确"
        )
        assert visibility_hook.get("pass_filenames") is True, "request-id-visibility-gate 应接收文件名参数"
        assert visibility_hook.get("stages") == ["pre-commit"], "request-id-visibility-gate stages 不正确"
        assert "python scripts/compliance/request_id_visibility_gate.py --format text" in visibility_hook.get(
            "entry", ""
        ), "request-id-visibility-gate entry 不正确"

        print("  ✅ Request ID visibility gate 本地钩子验证通过")

    def test_16_backend_singleton_none_guard_local_hook(self):
        """测试16: 验证后端单例 None guard 已接入本地钩子"""
        print("\n📍 测试16: 验证后端单例 None guard 本地钩子")
        local_repos = self._find_repos("local")
        singleton_hook = None

        for repo in local_repos:
            for hook in repo.get("hooks", []):
                if hook.get("id") == "backend-singleton-none-guard":
                    singleton_hook = hook
                    break
            if singleton_hook is not None:
                break

        assert singleton_hook is not None, "未找到'backend-singleton-none-guard'本地钩子"
        assert singleton_hook.get("name") == "Backend Singleton None Guard", "backend-singleton-none-guard 名称不正确"
        assert singleton_hook.get("language") == "system", "backend-singleton-none-guard 语言类型不正确"
        assert singleton_hook.get("files") == r"^((src/)|(web/backend/app/)).*\.py$", (
            "backend-singleton-none-guard 文件范围不正确"
        )
        assert singleton_hook.get("pass_filenames") is True, "backend-singleton-none-guard 应接收文件名参数"
        assert singleton_hook.get("stages") == ["pre-commit"], "backend-singleton-none-guard stages 不正确"
        assert "python scripts/compliance/backend_singleton_none_guard.py --format text" in singleton_hook.get(
            "entry", ""
        ), "backend-singleton-none-guard entry 不正确"

        print("  ✅ 后端单例 None guard 本地钩子验证通过")

    def test_17_unified_response_contract_guard_local_hook(self):
        """测试17: 验证 UnifiedResponse contract guard 已接入本地钩子"""
        print("\n📍 测试17: 验证 UnifiedResponse contract guard 本地钩子")
        local_repos = self._find_repos("local")
        contract_hook = None

        for repo in local_repos:
            for hook in repo.get("hooks", []):
                if hook.get("id") == "unified-response-contract-guard":
                    contract_hook = hook
                    break
            if contract_hook is not None:
                break

        assert contract_hook is not None, "未找到'unified-response-contract-guard'本地钩子"
        assert contract_hook.get("name") == "UnifiedResponse Contract Guard", (
            "unified-response-contract-guard 名称不正确"
        )
        assert contract_hook.get("language") == "system", "unified-response-contract-guard 语言类型不正确"
        assert contract_hook.get("files") == r"^web/backend/app/api/.*\.py$", (
            "unified-response-contract-guard 文件范围不正确"
        )
        assert contract_hook.get("pass_filenames") is True, "unified-response-contract-guard 应接收文件名参数"
        assert contract_hook.get("stages") == ["pre-commit"], "unified-response-contract-guard stages 不正确"
        assert "python scripts/compliance/unified_response_contract_guard.py --format text" in contract_hook.get(
            "entry", ""
        ), "unified-response-contract-guard entry 不正确"

        print("  ✅ UnifiedResponse contract guard 本地钩子验证通过")

    def test_18_frontend_test_file_size_guard_local_hook(self):
        """测试18: 验证前端 / 测试文件大小门禁已接入本地钩子"""
        print("\n📍 测试18: 验证前端 / 测试文件大小门禁本地钩子")
        local_repos = self._find_repos("local")
        file_size_hook = None

        for repo in local_repos:
            for hook in repo.get("hooks", []):
                if hook.get("id") == "frontend-test-file-size-guard":
                    file_size_hook = hook
                    break
            if file_size_hook is not None:
                break

        assert file_size_hook is not None, "未找到'frontend-test-file-size-guard'本地钩子"
        assert file_size_hook.get("name") == "Frontend/Test File Size Guard", (
            "frontend-test-file-size-guard 名称不正确"
        )
        assert file_size_hook.get("language") == "system", "frontend-test-file-size-guard 语言类型不正确"
        assert file_size_hook.get("files") == r"^((web/frontend/.*\.(vue|ts|js))|(tests/.*\.(ts|js)))$", (
            "frontend-test-file-size-guard 文件范围不正确"
        )
        assert file_size_hook.get("pass_filenames") is True, "frontend-test-file-size-guard 应接收文件名参数"
        assert file_size_hook.get("stages") == ["pre-commit"], "frontend-test-file-size-guard stages 不正确"
        assert "python scripts/compliance/file_size_guardrail.py --format text" in file_size_hook.get(
            "entry", ""
        ), "frontend-test-file-size-guard entry 不正确"

        print("  ✅ 前端 / 测试文件大小门禁本地钩子验证通过")

    def test_19_pm2_first_class_gate_local_hook(self):
        """测试19: 验证 PM2 一等公民门禁已接入本地钩子"""
        print("\n📍 测试19: 验证 PM2 一等公民门禁本地钩子")
        local_repos = self._find_repos("local")
        pm2_hook = None

        for repo in local_repos:
            for hook in repo.get("hooks", []):
                if hook.get("id") == "pm2-first-class-gate":
                    pm2_hook = hook
                    break
            if pm2_hook is not None:
                break

        assert pm2_hook is not None, "未找到'pm2-first-class-gate'本地钩子"
        assert pm2_hook.get("name") == "PM2 First-Class Gate", "pm2-first-class-gate 名称不正确"
        assert pm2_hook.get("language") == "system", "pm2-first-class-gate 语言类型不正确"
        assert pm2_hook.get("pass_filenames") is True, "pm2-first-class-gate 应接收文件名参数"
        assert pm2_hook.get("stages") == ["pre-commit"], "pm2-first-class-gate stages 不正确"
        assert "python scripts/compliance/pm2_first_class_gate.py --format text" in pm2_hook.get(
            "entry", ""
        ), "pm2-first-class-gate entry 不正确"

        print("  ✅ PM2 一等公民门禁本地钩子验证通过")


# if __name__ == "__main__":
#     pytest.main([__file__])
