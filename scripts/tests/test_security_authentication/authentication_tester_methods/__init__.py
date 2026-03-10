"""AuthenticationTester 方法级拆分包"""
from .part1 import AuthenticationTesterCoreMixin
from .part2 import AuthenticationTesterTestPasswordResetMixin
from .part3 import AuthenticationTesterAccessControlMfaMixin


class AuthenticationTester(
    AuthenticationTesterCoreMixin,
    AuthenticationTesterTestPasswordResetMixin,
    AuthenticationTesterAccessControlMfaMixin,
):
    """AuthenticationTester - 组合所有方法集"""
    pass


__all__ = ["AuthenticationTester"]
