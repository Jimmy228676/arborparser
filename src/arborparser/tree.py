from enum import Enum
from typing import Callable, Dict, List, Any
from arborparser.node import ChainNode, TreeNode
import json
from pathlib import Path


class TreeBuilder:
    class Strategy(Enum):
        """构建树的策略"""

        STRICT = "strict"
        BEST_FIT = "best_fit"

    def __init__(self, strategy: "TreeBuilder.Strategy" = Strategy.BEST_FIT):
        self.strategy = strategy
        self.strategy_map: Dict[
            "TreeBuilder.Strategy", Callable[[List[ChainNode]], TreeNode]
        ] = {
            self.Strategy.STRICT: self.strict_build,
            self.Strategy.BEST_FIT: self.best_fit_build,
        }
        # 确保所有枚举值都映射到策略方法
        assert set(self.strategy_map.keys()) == set(TreeBuilder.Strategy), (
            f"Not all strategies are mapped. Missing: "
            f"{set(TreeBuilder.Strategy) - set(self.strategy_map.keys())}"
        )

    def build_tree(self, chain: List[ChainNode]) -> TreeNode:
        return self.strategy_map[self.strategy](chain)

    def strict_build(self, chain: List[ChainNode]) -> TreeNode:
        """将链式节点转换为树形结构"""

        def _is_child(parent_seq: List[int], child_seq: List[int]) -> bool:
            """判断child是否是parent的直接子节点"""
            return (
                len(child_seq) == len(parent_seq) + 1 and child_seq[:-1] == parent_seq
            )

        root = TreeNode(level_seq=[], level_text="", title="ROOT")
        self._stack = [root]  # 当前层级路径栈

        for node in chain:
            new_tree_node = TreeNode(
                level_seq=node.level_seq,
                level_text=node.level_text,
                title=node.title,
                content=node.content,
            )

            # 寻找适当父节点的逻辑
            parent = root  # 默认父节点为根
            while self._stack:
                candidate = self._stack[-1]
                if _is_child(candidate.level_seq, new_tree_node.level_seq):
                    parent = candidate
                    break
                self._stack.pop()

            parent.children.append(new_tree_node)
            new_tree_node.parent = parent
            self._stack.append(new_tree_node)

        return root

    def best_fit_build(self, chain: List[ChainNode]) -> TreeNode:
        """容错模式下的树形结构构建，尝试将不规则的节点放置到最合适的位置"""

        def _find_best_parent(node: TreeNode, level_seq: List[int]) -> TreeNode:
            """查找最佳父节点，返回层级序列最匹配的节点"""
            if not level_seq:
                return node

            from collections import deque

            queue = deque([node])
            best_match = node
            best_match_length = 0

            while queue:
                current = queue.popleft()

                # 检查当前节点是否是更好的父节点匹配
                # 1. 当前节点必须有层级序列
                # 2. 当前节点的层级序列长度必须小于目标序列
                # 3. 当前节点的层级序列必须是目标序列的前缀
                # 4. 当前节点的层级序列必须比之前找到的匹配更长
                if (
                    current.level_seq
                    and len(current.level_seq) < len(level_seq)
                    and current.level_seq == level_seq[: len(current.level_seq)]
                    and len(current.level_seq) > best_match_length
                ):
                    best_match = current
                    best_match_length = len(current.level_seq)

                # 继续搜索子节点
                queue.extend(current.children)

            return best_match

        root = TreeNode(level_seq=[], level_text="", title="ROOT")

        for node in chain:
            new_tree_node = TreeNode(
                level_seq=node.level_seq,
                level_text=node.level_text,
                title=node.title,
                content=node.content,
            )

            # 找到最佳父节点并添加新节点
            parent = _find_best_parent(root, node.level_seq)
            new_tree_node.parent = parent
            parent.children.append(new_tree_node)

        return root


class TreeExporter:
    @staticmethod
    def export_chain(chain: List[ChainNode]) -> str:
        return "\n".join(f"LEVEL-{n.level_seq}: {n.title}" for n in chain)

    @staticmethod
    def export_tree(tree: TreeNode) -> str:
        return TreeExporter._export_tree_internal(tree)

    @staticmethod
    def _export_tree_internal(
        node: TreeNode, prefix: str = "", is_last: bool = False, is_root: bool = True
    ) -> str:
        """递归输出树形结构"""
        lines = []

        # 处理根节点特殊显示
        if is_root:
            lines.append(node.title)
            prefix = ""
        else:
            # 非根节点，生成连接符号
            connector = "└─ " if is_last else "├─ "
            lines.append(f"{prefix}{connector}{node.level_text} {node.title}")

        # 生成子节点前缀
        child_prefix = prefix
        if not is_root:
            child_prefix += "    " if is_last else "│   "

        # 递归处理子节点
        for i, child in enumerate(node.children):
            is_child_last = i == len(node.children) - 1
            lines.append(
                TreeExporter._export_tree_internal(
                    child, child_prefix, is_child_last, False
                )
            )

        return "\n".join(lines)

    @staticmethod
    def export_to_json(tree: TreeNode) -> str:
        """将树结构导出为JSON字符串"""
        return json.dumps(
            TreeExporter._node_to_dict(tree), ensure_ascii=False, indent=4
        )

    @staticmethod
    def export_to_json_file(tree: TreeNode, file_path: str | Path) -> None:
        """将树结构导出到JSON文件"""
        file_path = Path(file_path)
        json_data = TreeExporter.export_to_json(tree)
        file_path.write_text(json_data, encoding="utf-8")

    @staticmethod
    def _node_to_dict(node: TreeNode) -> Dict[str, Any]:
        """将节点转换为字典格式"""
        return {
            "title": node.title,
            "level_seq": node.level_seq,
            "level_text": node.level_text,
            "children": [TreeExporter._node_to_dict(child) for child in node.children],
        }
