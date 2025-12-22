"""
T0XX: Pylint配置验证单元测试

验证.pylintrc配置文件的完整性和正确性,
包括配置结构、禁用消息、行长度限制等。

创建日期: 2025-12-23
版本: 1.0.0
"""

import os
import configparser
import pytest


class TestPylintConfig:
    """Pylint配置验证测试类"""

    @classmethod
    def setup_class(cls):
        """测试类初始化：读取并解析.pylintrc文件"""
        cls.pylintrc_path = ".pylintrc"
        assert os.path.exists(cls.pylintrc_path), (
            f"Pylint配置文件不存在: {cls.pylintrc_path}"
        )

        cls.config = configparser.ConfigParser()
        cls.config.read(cls.pylintrc_path)

    def test_01_sections_exist(self):
        """测试1: 验证Pylint配置文件中的必需节是否存在"""
        print("📍 测试1: 验证Pylint配置文件中的必需节是否存在")
        expected_sections = [
            "MASTER",
            "MESSAGES CONTROL",
            "FORMAT",
            "DESIGN",
            "TYPECHECK",
            "SIMILARITIES",
        ]
        for section in expected_sections:
            assert self.config.has_section(section), f"缺少必需的节: [{section}]"
        print("  ✅ 必需的Pylint节验证通过")

    def test_02_master_options(self):
        """测试2: 验证MASTER节中的关键选项"""
        print("\n📍 测试2: 验证MASTER节中的关键选项")
        master_section = self.config["MASTER"]
        assert "extension-pkg-whitelist" in master_section, (
            "MASTER节缺少'extension-pkg-whitelist'选项"
        )
        assert master_section["extension-pkg-whitelist"].strip() != "", (
            "'extension-pkg-whitelist'选项不应为空"
        )
        assert "ignore" in master_section, "MASTER节缺少'ignore'选项"
        assert master_section["ignore"].strip() != "", "'ignore'选项不应为空"
        print("  ✅ MASTER节中的关键选项验证通过")

    def test_03_messages_control_disable(self):
        """测试3: 验证MESSAGES CONTROL节中的禁用消息"""
        print("\n📍 测试3: 验证MESSAGES CONTROL节中的禁用消息")
        messages_control_section = self.config["MESSAGES CONTROL"]
        assert "disable" in messages_control_section, (
            "MESSAGES CONTROL节缺少'disable'选项"
        )
        raw_disable_string = messages_control_section["disable"]
        disabled_messages = []
        for line in raw_disable_string.splitlines():
            for item in line.split(","):
                code_part = item.split("#")[0].strip()
                if code_part:
                    disabled_messages.append(code_part)

        expected_disabled_messages = [
            "C0114",
            "C0115",
            "C0116",
            "C0301",
            "C0103",
            "W0511",
            "W0612",
            "W0613",
            "R0903",
            "R0913",
            "R0914",
            "R0915",
            "E0401",
        ]

        for msg_code in expected_disabled_messages:
            assert msg_code in disabled_messages, (
                f"'disable'选项中缺少预期的禁用消息: {msg_code}"
            )
        print("  ✅ MESSAGES CONTROL节中的禁用消息验证通过")

    def test_04_format_max_line_length(self):
        """测试4: 验证FORMAT节中的max-line-length"""
        print("\n📍 测试4: 验证FORMAT节中的max-line-length")
        format_section = self.config["FORMAT"]
        assert "max-line-length" in format_section, "FORMAT节缺少'max-line-length'选项"

        try:
            max_line_length = int(format_section["max-line-length"])
            assert max_line_length == 120, (
                f"max-line-length的值不正确，预期为120，实际为{max_line_length}"
            )
        except ValueError:
            pytest.fail("max-line-length的值不是一个有效的整数")
        print("  ✅ FORMAT节中的max-line-length验证通过")


# if __name__ == "__main__":
#     # This block is for direct execution and will run all tests in this file
#     pytest.main([__file__])
