"""
代码相似性检测 - 识别重复和相似代码

使用混合方法：token-based 相似度 + AST 结构相似度

作者: MyStocks Team
日期: 2025-10-19
"""

import ast
import hashlib
from difflib import SequenceMatcher
from typing import List, Tuple, Optional
from pathlib import Path

import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from models import (
    CodeBlock,
    DuplicationCase,
    SeverityEnum,
    FunctionMetadata,
    severity_from_similarity,
)
from src.utils.ast_parser import tokenize_code, extract_code_block


class SimilarityDetector:
    """代码相似性检测器"""

    def __init__(
        self, min_token_similarity: float = 0.4, min_ast_similarity: float = 0.3
    ):
        """
        初始化相似性检测器

        Args:
            min_token_similarity: 最小 token 相似度阈值（0.0-1.0）
            min_ast_similarity: 最小 AST 相似度阈值（0.0-1.0）
        """
        self.min_token_similarity = min_token_similarity
        self.min_ast_similarity = min_ast_similarity

    def calculate_token_similarity(self, code1: str, code2: str) -> float:
        """
        计算两段代码的 token 相似度

        Args:
            code1: 第一段代码
            code2: 第二段代码

        Returns:
            相似度分数（0.0-1.0）
        """
        tokens1 = tokenize_code(code1)
        tokens2 = tokenize_code(code2)

        if not tokens1 or not tokens2:
            return 0.0

        # 使用 SequenceMatcher 计算序列相似度
        matcher = SequenceMatcher(None, tokens1, tokens2)
        return matcher.ratio()

    def calculate_ast_similarity(self, code1: str, code2: str) -> float:
        """
        计算两段代码的 AST 结构相似度

        Args:
            code1: 第一段代码
            code2: 第二段代码

        Returns:
            相似度分数（0.0-1.0）
        """
        try:
            tree1 = ast.parse(code1)
            tree2 = ast.parse(code2)

            # 计算 AST 结构哈希
            hash1 = self._ast_structure_hash(tree1)
            hash2 = self._ast_structure_hash(tree2)

            # 如果结构完全相同
            if hash1 == hash2:
                return 1.0

            # 比较 AST 节点序列
            nodes1 = self._extract_node_sequence(tree1)
            nodes2 = self._extract_node_sequence(tree2)

            if not nodes1 or not nodes2:
                return 0.0

            matcher = SequenceMatcher(None, nodes1, nodes2)
            return matcher.ratio()

        except SyntaxError:
            return 0.0

    def _ast_structure_hash(self, tree: ast.AST) -> str:
        """
        计算 AST 结构哈希（忽略标识符名称）

        Args:
            tree: AST 树

        Returns:
            哈希字符串
        """
        structure = []

        for node in ast.walk(tree):
            # 只记录节点类型，不记录具体值
            node_type = type(node).__name__
            structure.append(node_type)

            # 对特定节点类型记录额外信息
            if isinstance(node, ast.FunctionDef):
                structure.append(f"func_{len(node.args.args)}_args")
            elif isinstance(node, ast.ClassDef):
                structure.append(f"class_{len(node.bases)}_bases")
            elif isinstance(node, ast.For):
                structure.append("loop_for")
            elif isinstance(node, ast.While):
                structure.append("loop_while")

        # 生成哈希
        structure_str = "".join(structure)
        return hashlib.md5(structure_str.encode()).hexdigest()

    def _extract_node_sequence(self, tree: ast.AST) -> List[str]:
        """
        提取 AST 节点类型序列

        Args:
            tree: AST 树

        Returns:
            节点类型列表
        """
        sequence = []

        for node in ast.walk(tree):
            sequence.append(type(node).__name__)

        return sequence

    def compare_functions(
        self,
        func1: FunctionMetadata,
        func2: FunctionMetadata,
        file1_path: str,
        file2_path: str,
    ) -> Optional[Tuple[float, float]]:
        """
        比较两个函数的相似度

        Args:
            func1: 第一个函数元数据
            func2: 第二个函数元数据
            file1_path: 第一个文件路径
            file2_path: 第二个文件路径

        Returns:
            (token_similarity, ast_similarity) 或 None
        """
        # 提取函数代码
        code1 = extract_code_block(
            file1_path, func1.line_number, func1.line_number + func1.body_lines
        )
        code2 = extract_code_block(
            file2_path, func2.line_number, func2.line_number + func2.body_lines
        )

        if not code1 or not code2:
            return None

        # 计算相似度
        token_sim = self.calculate_token_similarity(code1, code2)
        ast_sim = self.calculate_ast_similarity(code1, code2)

        # 检查是否超过阈值
        if (
            token_sim >= self.min_token_similarity
            and ast_sim >= self.min_ast_similarity
        ):
            return (token_sim, ast_sim)

        return None

    def create_duplication_case(
        self,
        blocks: List[
            Tuple[str, int, int, str]
        ],  # (file_path, start_line, end_line, code)
        token_similarity: float,
        ast_similarity: float,
        description: str = "",
    ) -> DuplicationCase:
        """
        创建重复案例

        Args:
            blocks: 代码块列表，每个元素为 (file_path, start_line, end_line, code)
            token_similarity: Token 相似度
            ast_similarity: AST 相似度
            description: 描述

        Returns:
            DuplicationCase 对象
        """
        # 创建 CodeBlock 对象
        code_blocks = []
        affected_files = []

        for file_path, start_line, end_line, code in blocks:
            tokens = tokenize_code(code)
            try:
                tree = ast.parse(code)
                ast_hash = self._ast_structure_hash(tree)
            except:
                ast_hash = None

            code_blocks.append(
                CodeBlock(
                    file_path=file_path,
                    start_line=start_line,
                    end_line=end_line,
                    content=code,
                    tokens=tokens,
                    ast_hash=ast_hash,
                )
            )

            if file_path not in affected_files:
                affected_files.append(file_path)

        # 确定严重性
        severity = severity_from_similarity(token_similarity, ast_similarity)

        # 生成 ID
        dup_id = f"DUP-{hashlib.md5(f'{affected_files[0]}_{code_blocks[0].start_line}'.encode()).hexdigest()[:8]}"

        # 生成合并建议
        merge_suggestion = self._generate_merge_suggestion(severity, code_blocks)

        return DuplicationCase(
            id=dup_id,
            severity=severity,
            blocks=code_blocks,
            token_similarity=token_similarity,
            ast_similarity=ast_similarity,
            description=description or f"检测到 {len(code_blocks)} 处相似代码",
            merge_suggestion=merge_suggestion,
            affected_files=affected_files,
        )

    def _generate_merge_suggestion(
        self, severity: SeverityEnum, blocks: List[CodeBlock]
    ) -> str:
        """生成合并建议"""
        if severity == SeverityEnum.CRITICAL:
            return (
                "建议立即合并：代码几乎完全相同。\n"
                "1. 提取公共函数到共享工具模块\n"
                "2. 在原位置调用公共函数\n"
                "3. 删除重复代码"
            )
        elif severity == SeverityEnum.HIGH:
            return (
                "建议优先合并：代码高度相似。\n"
                "1. 识别差异部分并参数化\n"
                "2. 创建统一函数接受可变参数\n"
                "3. 重构调用点使用新函数"
            )
        elif severity == SeverityEnum.MEDIUM:
            return (
                "建议考虑合并：代码存在显著相似性。\n"
                "1. 分析差异是否可以通过配置或参数处理\n"
                "2. 评估合并的成本收益\n"
                "3. 如果合适，创建抽象基类或模板方法"
            )
        else:
            return (
                "可选优化：代码有一定相似性。\n"
                "1. 检查是否有共同的设计模式可以应用\n"
                "2. 考虑提取小的通用辅助函数\n"
                "3. 添加文档说明设计意图"
            )

    def find_similar_code_blocks(
        self, code_blocks: List[Tuple[str, int, int, str]]
    ) -> List[DuplicationCase]:
        """
        在代码块列表中查找相似项

        Args:
            code_blocks: 代码块列表

        Returns:
            重复案例列表
        """
        duplications = []
        processed = set()

        for i in range(len(code_blocks)):
            if i in processed:
                continue

            file1, start1, end1, code1 = code_blocks[i]
            similar_blocks = [(file1, start1, end1, code1)]

            for j in range(i + 1, len(code_blocks)):
                if j in processed:
                    continue

                file2, start2, end2, code2 = code_blocks[j]

                # 计算相似度
                token_sim = self.calculate_token_similarity(code1, code2)
                ast_sim = self.calculate_ast_similarity(code1, code2)

                if (
                    token_sim >= self.min_token_similarity
                    and ast_sim >= self.min_ast_similarity
                ):
                    similar_blocks.append((file2, start2, end2, code2))
                    processed.add(j)

            # 如果找到相似代码
            if len(similar_blocks) > 1:
                # 计算平均相似度（与第一个块比较）
                avg_token_sim = sum(
                    self.calculate_token_similarity(code_blocks[i][3], block[3])
                    for block in similar_blocks[1:]
                ) / (len(similar_blocks) - 1)

                avg_ast_sim = sum(
                    self.calculate_ast_similarity(code_blocks[i][3], block[3])
                    for block in similar_blocks[1:]
                ) / (len(similar_blocks) - 1)

                dup = self.create_duplication_case(
                    similar_blocks,
                    avg_token_sim,
                    avg_ast_sim,
                    f"检测到 {len(similar_blocks)} 处相似代码",
                )
                duplications.append(dup)
                processed.add(i)

        return duplications


def normalize_code(code: str) -> str:
    """
    标准化代码以便更好地比较

    Args:
        code: 原始代码

    Returns:
        标准化后的代码
    """
    import re

    # 移除注释
    code = re.sub(r"#.*$", "", code, flags=re.MULTILINE)

    # 移除空行
    lines = [line for line in code.split("\n") if line.strip()]

    # 标准化空白
    normalized_lines = []
    for line in lines:
        # 保留缩进结构，但标准化为 4 空格
        indent_level = len(line) - len(line.lstrip())
        indent_level = (indent_level // 4) * 4
        normalized_line = " " * indent_level + line.strip()
        normalized_lines.append(normalized_line)

    return "\n".join(normalized_lines)


if __name__ == "__main__":
    # 测试代码
    detector = SimilarityDetector()

    # 测试相似度计算
    code1 = """
def save_data(data, table_name):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"INSERT INTO {table_name} VALUES (?)", data)
    conn.commit()
    conn.close()
"""

    code2 = """
def store_info(info, table):
    connection = get_connection()
    cur = connection.cursor()
    cur.execute(f"INSERT INTO {table} VALUES (?)", info)
    connection.commit()
    connection.close()
"""

    token_sim = detector.calculate_token_similarity(code1, code2)
    ast_sim = detector.calculate_ast_similarity(code1, code2)

    print(f"Token similarity: {token_sim:.2%}")
    print(f"AST similarity: {ast_sim:.2%}")
    print(f"Severity: {severity_from_similarity(token_sim, ast_sim)}")
