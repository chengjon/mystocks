# scripts/dev/cli_config_manager.py

"""
CLI配置管理器 - 配置驱动的Multi-CLI管理

功能：
1. 读取和解析config.yaml
2. 提供CLI定义查询接口
3. 智能任务分配（支持技能匹配、范围匹配）
4. 交互式任务分配确认
5. 跨项目配置支持
"""

import sys
import os
import re
import yaml
from pathlib import Path
from typing import List, Dict, Optional, Tuple

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class CLIConfigManager:
    """CLI配置管理器"""

    def __init__(self, config_file="CLIS/config.yaml"):
        self.config_file = Path(config_file)
        self.config = self._load_config()

    def _load_config(self) -> dict:
        """加载配置文件"""
        if not self.config_file.exists():
            print(f"⚠️  配置文件不存在: {self.config_file}")
            print("使用默认配置")
            return self._get_default_config()

        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)

            print(f"✅ 已加载配置文件: {self.config_file}")
            print(f"   项目: {config['multi_cli']['project_name']}")
            print(f"   分配模式: {config['multi_cli']['task_assignment_mode']}")

            return config
        except Exception as e:
            print(f"❌ 配置文件加载失败: {e}")
            print("使用默认配置")
            return self._get_default_config()

    def _get_default_config(self) -> dict:
        """获取默认配置"""
        return {
            'multi_cli': {
                'version': '2.1',
                'project_name': 'default',
                'task_assignment_mode': 'auto',
                'auto_coordinate': True
            },
            'cli_definitions': {
                'main': {
                    'enabled': True,
                    'type': 'coordinator',
                    'capabilities': ['coordination', 'monitoring']
                },
                'web': {
                    'enabled': True,
                    'type': 'worker',
                    'capabilities': ['frontend']
                },
                'api': {
                    'enabled': True,
                    'type': 'worker',
                    'capabilities': ['backend']
                },
                'db': {
                    'enabled': True,
                    'type': 'worker',
                    'capabilities': ['database']
                }
            },
            'assignment_rules': [
                {'name': 'skill_based_assignment', 'enabled': True, 'priority': 1}
            ]
        }

    def get_enabled_clis(self) -> List[str]:
        """获取所有启用的CLI名称"""
        cli_defs = self.config.get('cli_definitions', {})
        enabled_clis = []

        for cli_name, cli_config in cli_defs.items():
            if cli_config.get('enabled', False):
                enabled_clis.append(cli_name)

        return enabled_clis

    def get_cli_info(self, cli_name: str) -> Optional[dict]:
        """获取CLI的完整配置信息"""
        cli_defs = self.config.get('cli_definitions', {})
        return cli_defs.get(cli_name)

    def get_cli_capabilities(self, cli_name: str) -> List[str]:
        """获取CLI的能力列表"""
        cli_info = self.get_cli_info(cli_name)
        if not cli_info:
            return []
        return cli_info.get('capabilities', [])

    def get_cli_task_scope(self, cli_name: str) -> dict:
        """获取CLI的任务范围配置"""
        cli_info = self.get_cli_info(cli_name)
        if not cli_info:
            return {'include': ['*'], 'exclude': []}
        return cli_info.get('task_scope', {'include': ['*'], 'exclude': []})

    def match_task_to_cli(self, task_id: str, task_skills: List[str]) -> List[str]:
        """
        匹配任务到合适的CLI

        Args:
            task_id: 任务ID
            task_skills: 任务需要的技能列表

        Returns:
            匹配的CLI名称列表（按优先级排序）
        """
        matched_clis = []

        for cli_name in self.get_enabled_clis():
            if cli_name == 'main':
                continue  # 跳过协调器本身

            cli_info = self.get_cli_info(cli_name)
            if not cli_info:
                continue

            # 检查任务范围是否匹配
            if not self._check_task_scope(cli_name, task_id):
                continue

            # 检查技能是否匹配
            cli_capabilities = cli_info.get('capabilities', [])
            skill_match_score = self._calculate_skill_match(task_skills, cli_capabilities)

            if skill_match_score > 0:
                matched_clis.append({
                    'name': cli_name,
                    'score': skill_match_score,
                    'capabilities': cli_capabilities,
                    'role': cli_info.get('role', 'worker')
                })

        # 按匹配分数排序
        matched_clis.sort(key=lambda x: x['score'], reverse=True)

        return [cli['name'] for cli in matched_clis]

    def _check_task_scope(self, cli_name: str, task_id: str) -> bool:
        """检查任务是否在CLI的任务范围内"""
        task_scope = self.get_cli_task_scope(cli_name)

        # 检查include规则
        included = False
        for pattern in task_scope.get('include', ['*']):
            if re.match(pattern.replace('*', '.*'), task_id):
                included = True
                break

        if not included:
            return False

        # 检查exclude规则
        for pattern in task_scope.get('exclude', []):
            if re.match(pattern.replace('*', '.*'), task_id):
                return False

        return True

    def _calculate_skill_match(self, task_skills: List[str], cli_capabilities: List[str]) -> int:
        """计算技能匹配分数"""
        score = 0
        for skill in task_skills:
            if skill in cli_capabilities:
                score += 1
        return score

    def suggest_cli_for_task(self, task_id: str, task_data: dict) -> Tuple[List[str], str]:
        """
        为任务建议合适的CLI

        Args:
            task_id: 任务ID
            task_data: 任务数据（包含title, skills, priority等）

        Returns:
            (建议的CLI列表, 建议理由)
        """
        task_skills = task_data.get('skills', [])
        task_priority = task_data.get('priority', 'MEDIUM')

        # 匹配CLI
        matched_clis = self.match_task_to_cli(task_id, task_skills)

        if not matched_clis:
            return [], f"未找到匹配的CLI（任务技能: {task_skills}）"

        # 生成建议理由
        top_cli = matched_clis[0]
        top_cli_info = self.get_cli_info(top_cli)
        top_cli_role = top_cli_info.get('role', 'worker')

        reason = f"建议分配给 {top_cli}（角色: {top_cli_role}），"

        if len(task_skills) > 0:
            reason += f"技能匹配度: {len(task_skills)}/{len(task_skills)}，"

        if task_priority == 'HIGH':
            reason += "高优先级任务，"

        reason += f"任务ID {task_id} 在其任务范围内"

        return matched_clis, reason

    def interactive_confirm_assignment(self, task_id: str, task_data: dict, suggested_cli: str) -> bool:
        """
        交互式确认任务分配

        Args:
            task_id: 任务ID
            task_data: 任务数据
            suggested_cli: 建议的CLI名称

        Returns:
            是否确认分配
        """
        assignment_mode = self.config['multi_cli'].get('task_assignment_mode', 'auto')

        # 自动模式：直接确认
        if assignment_mode == 'auto':
            return True

        # 手动模式：直接拒绝（需要手动分配）
        if assignment_mode == 'manual':
            return False

        # 交互模式：询问用户
        if assignment_mode == 'interactive':
            return self._ask_user_confirmation(task_id, task_data, suggested_cli)

        return False

    def _ask_user_confirmation(self, task_id: str, task_data: dict, suggested_cli: str) -> bool:
        """询问用户确认任务分配"""
        import sys

        print("\n" + "="*60)
        print(f"📋 任务分配确认")
        print("="*60)
        print(f"任务ID: {task_id}")
        print(f"任务标题: {task_data.get('title', 'N/A')}")
        print(f"任务描述: {task_data.get('description', 'N/A')}")
        print(f"优先级: {task_data.get('priority', 'MEDIUM')}")
        print(f"需要技能: {', '.join(task_data.get('skills', []))}")
        print(f"建议分配给: {suggested_cli}")
        print("="*60)

        while True:
            response = input("是否确认分配？(y/n/e=edit/v=view_cli): ").strip().lower()

            if response in ['y', 'yes']:
                print(f"✅ 任务已分配给 {suggested_cli}")
                return True

            elif response in ['n', 'no']:
                print("❌ 已取消任务分配")
                return False

            elif response == 'v':
                # 查看CLI详情
                self._show_cli_details(suggested_cli)

            elif response == 'e':
                # 编辑分配
                new_cli = input("请输入要分配的CLI名称: ").strip()
                enabled_clis = self.get_enabled_clis()
                if new_cli in enabled_clis:
                    print(f"✅ 任务已分配给 {new_cli}")
                    return True
                else:
                    print(f"❌ 无效的CLI名称，可选: {', '.join(enabled_clis)}")

            else:
                print("无效输入，请输入 y/n/e/v")

    def _show_cli_details(self, cli_name: str):
        """显示CLI详细信息"""
        cli_info = self.get_cli_info(cli_name)
        if not cli_info:
            print(f"❌ CLI不存在: {cli_name}")
            return

        print(f"\n{'='*60}")
        print(f"CLI详细信息: {cli_name}")
        print(f"{'='*60}")
        print(f"类型: {cli_info.get('type', 'N/A')}")
        print(f"角色: {cli_info.get('role', 'N/A')}")
        print(f"描述: {cli_info.get('description', 'N/A')}")
        print(f"能力: {', '.join(cli_info.get('capabilities', []))}")

        task_scope = cli_info.get('task_scope', {})
        if task_scope:
            print(f"任务范围:")
            print(f"  包含: {task_scope.get('include', [])}")
            print(f"  排除: {task_scope.get('exclude', [])}")

        limits = cli_info.get('limits', {})
        if limits:
            print(f"工作限制:")
            print(f"  最大并发任务: {limits.get('max_concurrent_tasks', 'N/A')}")
            print(f"  最大任务工时: {limits.get('max_hours_per_task', 'N/A')}小时")

        print(f"{'='*60}\n")

    def get_assignment_mode(self) -> str:
        """获取任务分配模式"""
        return self.config['multi_cli'].get('task_assignment_mode', 'auto')

    def set_assignment_mode(self, mode: str):
        """设置任务分配模式"""
        if mode not in ['auto', 'interactive', 'manual']:
            raise ValueError(f"无效的分配模式: {mode}，可选: auto, interactive, manual")

        self.config['multi_cli']['task_assignment_mode'] = mode
        print(f"✅ 任务分配模式已设置为: {mode}")

    def export_config(self, output_file: str = None):
        """导出当前配置到文件"""
        if not output_file:
            output_file = self.config_file

        with open(output_file, 'w', encoding='utf-8') as f:
            yaml.dump(self.config, f, allow_unicode=True, default_flow_style=False)

        print(f"✅ 配置已导出到: {output_file}")

    def create_cli_from_template(self, cli_name: str, template: str = 'worker'):
        """从模板创建新CLI配置"""
        templates = {
            'worker': {
                'enabled': True,
                'type': 'worker',
                'role': f'{cli_name}_developer',
                'description': f'{cli_name} 开发助手',
                'capabilities': [],
                'task_scope': {'include': ['*'], 'exclude': []}
            },
            'coordinator': {
                'enabled': True,
                'type': 'coordinator',
                'description': f'{cli_name} 协调器',
                'capabilities': ['coordination', 'monitoring']
            }
        }

        if template not in templates:
            raise ValueError(f"无效的模板: {template}，可选: worker, coordinator")

        cli_defs = self.config.setdefault('cli_definitions', {})
        cli_defs[cli_name] = templates[template]

        print(f"✅ 已从模板 '{template}' 创建CLI配置: {cli_name}")
        print(f"   请编辑配置文件添加具体的能力和任务范围")

    def list_all_clis(self, show_disabled: bool = False) -> List[dict]:
        """列出所有CLI（包括禁用的）"""
        cli_list = []
        cli_defs = self.config.get('cli_definitions', {})

        for cli_name, cli_config in cli_defs.items():
            if not show_disabled and not cli_config.get('enabled', False):
                continue

            cli_list.append({
                'name': cli_name,
                'enabled': cli_config.get('enabled', False),
                'type': cli_config.get('type', 'worker'),
                'role': cli_config.get('role', 'N/A'),
                'capabilities': cli_config.get('capabilities', []),
                'description': cli_config.get('description', 'N/A')
            })

        return cli_list


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='CLI配置管理器')
    parser.add_argument('--config', default='CLIS/config.yaml', help='配置文件路径')
    parser.add_argument('--list', action='store_true', help='列出所有CLI')
    parser.add_argument('--show-disabled', action='store_true', help='显示禁用的CLI')
    parser.add_argument('--info', help='查看特定CLI的详细信息')
    parser.add_argument('--match', help='测试任务匹配（任务ID）')
    parser.add_argument('--skills', help='测试任务匹配（技能列表，逗号分隔）')
    parser.add_argument('--set-mode', choices=['auto', 'interactive', 'manual'], help='设置任务分配模式')
    parser.add_argument('--create-cli', help='从模板创建新CLI配置')
    parser.add_argument('--template', choices=['worker', 'coordinator'], default='worker', help='CLI模板类型')

    args = parser.parse_args()

    # 创建配置管理器
    manager = CLIConfigManager(args.config)

    if args.list:
        # 列出所有CLI
        cli_list = manager.list_all_clis(show_disabled=args.show_disabled)

        print(f"\n找到 {len(cli_list)} 个CLI:\n")
        for cli in cli_list:
            status = "✅" if cli['enabled'] else "❌"
            print(f"{status} {cli['name']}")
            print(f"   类型: {cli['type']}")
            print(f"   角色: {cli['role']}")
            print(f"   能力: {', '.join(cli['capabilities'])}")
            print(f"   描述: {cli['description']}")
            print()

    elif args.info:
        # 显示CLI详细信息
        manager._show_cli_details(args.info)

    elif args.match:
        # 测试任务匹配
        task_skills = args.skills.split(',') if args.skills else []

        matched_clis, reason = manager.suggest_cli_for_task(args.match, {
            'skills': task_skills,
            'priority': 'HIGH',
            'title': '测试任务'
        })

        print(f"\n任务: {args.match}")
        print(f"技能: {task_skills}")
        print(f"\n{reason}")
        print(f"\n匹配的CLI: {', '.join(matched_clis) if matched_clis else '无'}")

    elif args.set_mode:
        # 设置任务分配模式
        manager.set_assignment_mode(args.set_mode)
        manager.export_config()

    elif args.create_cli:
        # 从模板创建CLI
        manager.create_cli_from_template(args.create_cli, args.template)
        manager.export_config()

    else:
        # 显示配置概览
        print(f"\n{'='*60}")
        print(f"Multi-CLI 配置概览")
        print(f"{'='*60}")
        print(f"项目: {manager.config['multi_cli']['project_name']}")
        print(f"版本: {manager.config['multi_cli']['version']}")
        print(f"分配模式: {manager.config['multi_cli']['task_assignment_mode']}")
        print(f"自动协调: {'是' if manager.config['multi_cli']['auto_coordinate'] else '否'}")

        enabled_clis = manager.get_enabled_clis()
        print(f"\n已启用的CLI ({len(enabled_clis)}个):")
        for cli_name in enabled_clis:
            cli_info = manager.get_cli_info(cli_name)
            print(f"  - {cli_name}: {cli_info.get('role', 'N/A')}")

        print(f"\n💡 使用 --list 查看所有CLI详细信息")
        print(f"💡 使用 --info=CLI_NAME 查看特定CLI详情")
        print(f"💡 使用 --match=TASK_ID --skills=skill1,skill2 测试任务匹配")
        print(f"{'='*60}\n")


if __name__ == '__main__':
    main()
