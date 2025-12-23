"""
密码策略验证模块
实现强密码策略要求，包括：
- 最小长度要求
- 复杂度要求（大小写字母、数字、特殊字符）
- 常见密码检查
"""

import re
from typing import List, Dict, Tuple
import structlog

logger = structlog.get_logger()


class PasswordPolicy:
    """密码策略验证器"""

    def __init__(
        self,
        min_length: int = 12,
        require_uppercase: bool = True,
        require_lowercase: bool = True,
        require_digit: bool = True,
        require_special_char: bool = True,
        check_common_passwords: bool = True,
        max_length: int = 128,
    ):
        """
        初始化密码策略

        Args:
            min_length: 最小密码长度
            require_uppercase: 是否需要大写字母
            require_lowercase: 是否需要小写字母
            require_digit: 是否需要数字
            require_special_char: 是否需要特殊字符
            check_common_passwords: 是否检查常见密码
            max_length: 最大密码长度
        """
        self.min_length = min_length
        self.max_length = max_length
        self.require_uppercase = require_uppercase
        self.require_lowercase = require_lowercase
        self.require_digit = require_digit
        self.require_special_char = require_special_char
        self.check_common_passwords = check_common_passwords

        # 常见密码列表（简化版，生产环境应使用更完整的列表）
        self.common_passwords = {
            "password",
            "123456",
            "12345678",
            "123456789",
            "12345",
            "1234567",
            "1234567890",
            "qwerty",
            "abc123",
            "password123",
            "admin",
            "welcome",
            "monkey",
            "letmein",
            "dragon",
            "p@ssword",
            "iloveyou",
            "admin123",
            "password1",
            "master",
            "hello",
            "football",
            "charlie",
            "andrew",
            "michael",
            "jennifer",
            "111111",
            "888888",
            "000000",
            "password!",
            "password123!",
        }

    def validate_password(self, password: str) -> Tuple[bool, List[str]]:
        """
        验证密码是否符合策略

        Args:
            password: 要验证的密码

        Returns:
            Tuple[bool, List[str]]: (是否通过验证, 错误信息列表)
        """
        errors = []

        # 检查密码长度
        if len(password) < self.min_length:
            errors.append(f"密码长度必须至少为 {self.min_length} 个字符")
        elif len(password) > self.max_length:
            errors.append(f"密码长度不能超过 {self.max_length} 个字符")

        # 检查复杂性要求
        if self.require_uppercase and not re.search(r"[A-Z]", password):
            errors.append("密码必须包含至少一个大写字母")

        if self.require_lowercase and not re.search(r"[a-z]", password):
            errors.append("密码必须包含至少一个小写字母")

        if self.require_digit and not re.search(r"\d", password):
            errors.append("密码必须包含至少一个数字")

        if self.require_special_char and not re.search(
            r'[!@#$%^&*(),.?":{}|<>]', password
        ):
            errors.append('密码必须包含至少一个特殊字符 (!@#$%^&*(),.?":{}|<>)')

        # 检查常见密码
        if self.check_common_passwords:
            normalized_password = password.lower().strip()
            if normalized_password in self.common_passwords:
                errors.append("密码过于常见，请使用更复杂的密码")

            # 检查是否只是常见密码的简单变形
            if self._is_simple_variation(normalized_password):
                errors.append("密码过于简单，请避免使用常见密码的简单变形")

        # 检查重复字符
        if len(set(password.lower())) < 4:
            errors.append("密码包含过多重复字符")

        # 检查连续字符
        if self._has_consecutive_chars(password):
            errors.append("密码包含过多连续字符")

        # 检查键盘模式
        if self._is_keyboard_pattern(password.lower()):
            errors.append("密码不应使用键盘上的连续按键模式")

        return len(errors) == 0, errors

    def _is_simple_variation(self, password: str) -> bool:
        """检查是否是常见密码的简单变形"""
        common_patterns = [
            r"^\d+$",  # 纯数字
            r"^[a-z]+$",  # 纯小写
            r"^[a-z]+\d+$",  # 小写+数字
            r"^\d+[a-z]+$",  # 数字+小写
            r"^[a-z]+\d+!+$",  # 小写+数字+感叹号
        ]

        for pattern in common_patterns:
            if re.match(pattern, password):
                return True

        return False

    def _has_consecutive_chars(self, password: str) -> bool:
        """检查是否有过多连续字符"""
        for i in range(len(password) - 2):
            # 检查升序连续
            if (
                ord(password[i + 1]) - ord(password[i]) == 1
                and ord(password[i + 2]) - ord(password[i + 1]) == 1
            ):
                return True

            # 检查降序连续
            if (
                ord(password[i]) - ord(password[i + 1]) == 1
                and ord(password[i + 1]) - ord(password[i + 2]) == 1
            ):
                return True

        return False

    def _is_keyboard_pattern(self, password: str) -> bool:
        """检查是否是键盘模式"""
        keyboard_patterns = [
            "qwerty",
            "asdfgh",
            "zxcvbn",
            "123456",
            "654321",
            "qazwsx",
            "edcrfv",
            "tgbnhy",
            "yhnmgb",
            "ujmik",
            "ol.p;",
            "lo.p;",
            "p;.lo",
            "/.p;l",
            ";.l/p",
        ]

        for pattern in keyboard_patterns:
            if pattern in password or pattern[::-1] in password:
                return True

        return False

    def get_policy_description(self) -> Dict[str, any]:
        """获取密码策略描述"""
        return {
            "min_length": self.min_length,
            "max_length": self.max_length,
            "require_uppercase": self.require_uppercase,
            "require_lowercase": self.require_lowercase,
            "require_digit": self.require_digit,
            "require_special_char": self.require_special_char,
            "check_common_passwords": self.check_common_passwords,
            "description": (
                f"密码必须至少 {self.min_length} 个字符，最多 {self.max_length} 个字符，"
                f"包含大小写字母、数字和特殊字符，且不能是常见密码"
            ),
        }


class PasswordValidator:
    """密码验证器类"""

    def __init__(self):
        self.policy = PasswordPolicy()

    def validate(self, password: str) -> Tuple[bool, List[str]]:
        """验证密码"""
        return self.policy.validate_password(password)

    def validate_and_log(
        self, password: str, context: str = ""
    ) -> Tuple[bool, List[str]]:
        """验证密码并记录日志"""
        is_valid, errors = self.validate(password)

        if not is_valid:
            logger.warning(
                "密码验证失败",
                context=context,
                errors=errors,
                password_length=len(password),
            )
        else:
            logger.info("密码验证通过", context=context, password_length=len(password))

        return is_valid, errors

    def get_policy(self) -> PasswordPolicy:
        """获取密码策略"""
        return self.policy


# 全局验证器实例
_password_validator = None


def get_password_validator() -> PasswordValidator:
    """获取全局密码验证器实例"""
    global _password_validator
    if _password_validator is None:
        _password_validator = PasswordValidator()
    return _password_validator


def validate_password(password: str) -> Tuple[bool, List[str]]:
    """验证密码的便捷函数"""
    return get_password_validator().validate(password)


def validate_password_with_context(
    password: str, context: str = ""
) -> Tuple[bool, List[str]]:
    """验证密码并记录上下文信息的便捷函数"""
    return get_password_validator().validate_and_log(password, context)


def get_password_policy() -> Dict[str, any]:
    """获取密码策略信息的便捷函数"""
    return get_password_validator().get_policy().get_policy_description()


# 使用示例
if __name__ == "__main__":
    validator = get_password_validator()

    # 测试密码
    test_passwords = [
        "password",  # 太简单
        "12345678",  # 太简单
        "Password123",  # 缺少特殊字符
        "Password123!",  # 符合要求
        "P@ssw0rd",  # 太短
        "P@ssw0rdLongEnough123!",  # 符合要求
        "qwertyuiop",  # 键盘模式
    ]

    for password in test_passwords:
        is_valid, errors = validator.validate(password)
        print(f"密码: {password}")
        print(f"验证通过: {is_valid}")
        if errors:
            print(f"错误: {errors}")
        print("-" * 50)
