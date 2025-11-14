from typing import Dict, List, Any, Optional, Union, cast
from arborparser.node import ChainNode, TreeNode
import json
from pathlib import Path
from arborparser.build_strategy import TreeBuildingStrategy, AutoPruneStrategy


class TreeBuilder:
    """Class that builds a tree using a specified strategy."""

    def __init__(self, strategy: Optional[TreeBuildingStrategy] = None):
        """
        Initialize the TreeBuilder with a specified strategy.

        Args:
            strategy (TreeBuildingStrategy): An instance of a strategy to build the tree. None defaults to StrictStrategy.
        """
        if strategy is None:
            strategy = AutoPruneStrategy()  # default strategy

        self.strategy = strategy

    def build_tree(
        self, chain: Union[List[ChainNode], List[List[ChainNode]]]
    ) -> TreeNode:
        """
        Build a tree from a list of ChainNodes using the specified strategy.

        Args:
            chain (List[ChainNode] | List[List[ChainNode]]): Parsed chain data.

        Returns:
            TreeNode: The root of the constructed tree.
        """
        return self.strategy.build_tree(chain)


class TreeExporter:
    @staticmethod
    def export_chain(
        chain: Union[List[ChainNode], List[List[ChainNode]]]
    ) -> str:
        """
        Export the chain as a string.

        Args:
            chain (List[ChainNode] | List[List[ChainNode]]): ChainNodes or multi-candidate rows.

        Returns:
            str: Formatted string of the chain.
        """
        if not chain:
            return ""

        first = chain[0]
        if isinstance(first, ChainNode):
            return "\n".join(f"LEVEL-{n.level_seq}: {n.title}" for n in chain)  # type: ignore[list-item]

        multi_chain = cast(List[List[ChainNode]], chain)
        lines = []
        for candidates in multi_chain:
            inner = ", ".join(
                f"LEVEL-{node.level_seq}: {node.title}" for node in candidates
            )
            lines.append(f"[{inner}]")
        return "\n".join(lines)

    @staticmethod
    def export_tree(tree: TreeNode) -> str:
        """
        Export the tree as a formatted string.

        Args:
            tree (TreeNode): Root of the tree to export.

        Returns:
            str: Formatted string of the tree.
        """
        return TreeExporter._export_tree_internal(tree)

    @staticmethod
    def _export_tree_internal(
        node: TreeNode, prefix: str = "", is_last: bool = False, is_root: bool = True
    ) -> str:
        """
        Recursively output the tree structure.

        Args:
            node (TreeNode): Current node in the tree.
            prefix (str): Prefix string for the tree structure.
            is_last (bool): Flag indicating if the node is the last child.
            is_root (bool): Flag indicating if the node is the root.

        Returns:
            str: Formatted string of the tree structure.
        """
        lines = []

        if is_root:
            lines.append(node.title)
            prefix = ""
        else:
            connector = "└─ " if is_last else "├─ "
            lines.append(f"{prefix}{connector}{node.level_text} {node.title}")

        child_prefix = prefix
        if not is_root:
            child_prefix += "    " if is_last else "│   "

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
        """
        Export the tree structure to a JSON string.

        Args:
            tree (TreeNode): Root of the tree to export.

        Returns:
            str: JSON string representation of the tree.
        """
        return json.dumps(
            TreeExporter._node_to_dict(tree),
            ensure_ascii=False,
            indent=4,
        )

    @staticmethod
    def export_to_json_file(tree: TreeNode, file_path: Union[str, Path]) -> None:
        """
        Export the tree structure to a JSON file.

        Args:
            tree (TreeNode): Root of the tree to export.
            file_path (Union[str, Path]): Output file path.

        Returns:
            None
        """
        file_path = Path(file_path)
        json_data = TreeExporter.export_to_json(tree)
        file_path.write_text(json_data, encoding="utf-8")

    @staticmethod
    def _node_to_dict(node: TreeNode) -> Dict[str, Any]:
        """
        Convert a node to dictionary format.

        Args:
            node (TreeNode): Node to convert.

        Returns:
            Dict[str, Any]: Dictionary representation of the node.
        """
        return {
            "title": node.title,
            "level_seq": node.level_seq,
            "level_text": node.level_text,
            "content": node.content,
            "children": [TreeExporter._node_to_dict(child) for child in node.children],
        }
