#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Compliance control catalog extracted from `part1.py`."""

from ..helpers import ComplianceControl, ComplianceLevel, ComplianceStandard


def build_compliance_controls() -> list[ComplianceControl]:
    """构建合规控制项目录。"""
    controls = []

    gdpr_controls = [
        ComplianceControl(
            control_id="GDPR-PR-001",
            control_name="数据主体权利",
            description="确保用户能够访问、更正、删除其个人数据",
            standard=ComplianceStandard.GDPR,
            requirement_level="mandatory",
            test_method="test_user_data_rights",
            evidence_required=["用户数据访问日志", "数据删除确认", "数据修改记录"],
            implementation_status=ComplianceLevel.NOT_TESTED,
        ),
        ComplianceControl(
            control_id="GDPR-CON-001",
            control_name="数据处理同意",
            description="确保数据处理前获得明确同意",
            standard=ComplianceStandard.GDPR,
            requirement_level="mandatory",
            test_method="test_consent_mechanism",
            evidence_required=["同意记录", "撤回同意记录", "同意时间戳"],
            implementation_status=ComplianceLevel.NOT_TESTED,
        ),
        ComplianceControl(
            control_id="GDPR-DP-001",
            control_name="数据最小化",
            description="只收集和处理必要的数据",
            standard=ComplianceStandard.GDPR,
            requirement_level="mandatory",
            test_method="test_data_minimization",
            evidence_required=["数据收集清单", "数据保留策略", "数据生命周期记录"],
            implementation_status=ComplianceLevel.NOT_TESTED,
        ),
    ]

    pci_controls = [
        ComplianceControl(
            control_id="PCI-REQ-001",
            control_name="密码复杂度要求",
            description="实施强密码策略",
            standard=ComplianceStandard.PCI_DSS,
            requirement_level="mandatory",
            test_method="test_password_policy",
            evidence_required=["密码策略文档", "密码强度检查记录", "密码历史记录"],
            implementation_status=ComplianceLevel.NOT_TESTED,
        ),
        ComplianceControl(
            control_id="PCI-NET-001",
            control_name="网络分段",
            description="隔离网络组件和敏感数据",
            standard=ComplianceStandard.PCI_DSS,
            requirement_level="mandatory",
            test_method="test_network_segmentation",
            evidence_required=["网络架构图", "防火墙配置", "访问控制列表"],
            implementation_status=ComplianceLevel.NOT_TESTED,
        ),
        ComplianceControl(
            control_id="PCI-APP-001",
            control_name="应用安全",
            description="实施安全编码实践和漏洞管理",
            standard=ComplianceStandard.PCI_DSS,
            requirement_level="mandatory",
            test_method="test_application_security",
            evidence_required=["安全测试报告", "漏洞扫描记录", "修复记录"],
            implementation_status=ComplianceLevel.NOT_TESTED,
        ),
    ]

    sox_controls = [
        ComplianceControl(
            control_id="SOX-FC-001",
            control_name="财务完整性",
            description="确保财务数据的完整性和准确性",
            standard=ComplianceStandard.SOX,
            requirement_level="mandatory",
            test_method="test_financial_integrity",
            evidence_required=["数据完整性检查", "审计日志", "对账记录"],
            implementation_status=ComplianceLevel.NOT_TESTED,
        ),
        ComplianceControl(
            control_id="SOX-AU-001",
            control_name="访问控制",
            description="限制对财务系统的访问",
            standard=ComplianceStandard.SOX,
            requirement_level="mandatory",
            test_method="test_access_controls",
            evidence_required=["访问权限列表", "权限变更记录", "访问日志"],
            implementation_status=ComplianceLevel.NOT_TESTED,
        ),
        ComplianceControl(
            control_id="SOX-TR-001",
            control_name="交易完整性",
            description="确保交易记录的完整性和可追溯性",
            standard=ComplianceStandard.SOX,
            requirement_level="mandatory",
            test_method="test_transaction_integrity",
            evidence_required=["交易记录", "审计轨迹", "修改历史"],
            implementation_status=ComplianceLevel.NOT_TESTED,
        ),
    ]

    owasp_controls = [
        ComplianceControl(
            control_id="OWASP-A01-2021",
            control_name="失效的访问控制",
            description="验证访问控制机制的有效性",
            standard=ComplianceStandard.OWASP,
            requirement_level="mandatory",
            test_method="test_access_control_effectiveness",
            evidence_required=["访问测试结果", "权限验证记录", "绕过尝试记录"],
            implementation_status=ComplianceLevel.NOT_TESTED,
        ),
        ComplianceControl(
            control_id="OWASP-A02-2021",
            control_name="加密机制失效",
            description="验证数据加密实现",
            standard=ComplianceStandard.OWASP,
            requirement_level="mandatory",
            test_method="test_crypto_implementations",
            evidence_required=["加密算法文档", "密钥管理记录", "加密强度测试"],
            implementation_status=ComplianceLevel.NOT_TESTED,
        ),
        ComplianceControl(
            control_id="OWASP-A03-2021",
            control_name="注入",
            description="防止SQL注入、命令注入等",
            standard=ComplianceStandard.OWASP,
            requirement_level="mandatory",
            test_method="test_injection_prevention",
            evidence_required=["输入验证记录", "参数化查询使用", "注入测试结果"],
            implementation_status=ComplianceLevel.NOT_TESTED,
        ),
    ]

    controls.extend(gdpr_controls)
    controls.extend(pci_controls)
    controls.extend(sox_controls)
    controls.extend(owasp_controls)

    return controls
