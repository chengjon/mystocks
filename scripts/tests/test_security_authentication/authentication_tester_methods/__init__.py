"""AuthenticationTester 方法级拆分包"""
from .part1 import AuthenticationTesterCoreMixin
from .part2 import AuthenticationTesterTestPasswordResetMixin


class AuthenticationTester(
    AuthenticationTesterCoreMixin,
    AuthenticationTesterTestPasswordResetMixin,
):
    """AuthenticationTester - 组合所有方法集"""
    pass


__all__ = ["AuthenticationTester"]
