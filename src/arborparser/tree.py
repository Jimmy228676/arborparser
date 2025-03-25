from typing import Dict, List, Any, Optional, Union
from arborparser.node import ChainNode, TreeNode
import json
from pathlib import Path
from abc import ABC, abstractmethod


class TreeBuildingStrategy(ABC):
    """Abstract base class for tree building strategies."""

    @abstractmethod
    def build_tree(self, chain: List[ChainNode]) -> TreeNode:
        """
        Build a tree from a list of ChainNodes.

        Args:
            chain (List[ChainNode]): List of ChainNodes to be converted into a tree.

        Returns:
            TreeNode: The root of the constructed tree.
        """
        pass


class StrictStrategy(TreeBuildingStrategy):
    """Concrete implementation of a strict tree building strategy."""

    def build_tree(self, chain: List[ChainNode]) -> TreeNode:
        """
        Convert chain nodes to a tree structure using a strict strategy.

        Args:
            chain (List[ChainNode]): List of ChainNodes.

        Returns:
            TreeNode: The root of the constructed tree using strict rules.
        """

        def _is_child(parent_seq: List[int], child_seq: List[int]) -> bool:
            """Determine if child is a direct child of parent."""
            return (
                len(child_seq) == len(parent_seq) + 1 and child_seq[:-1] == parent_seq
            )

        root = TreeNode(level_seq=[], level_text="", title="ROOT")
        stack = [root]  # Current hierarchy path stack

        for node in chain:
            new_tree_node = TreeNode(
                level_seq=node.level_seq,
                level_text=node.level_text,
                title=node.title,
                content=node.content,
            )

            # Logic to find appropriate parent node
            parent = root  # Default parent node is root
            while stack:
                candidate = stack[-1]
                if _is_child(candidate.level_seq, new_tree_node.level_seq):
                    parent = candidate
                    break
                stack.pop()

            parent.children.append(new_tree_node)
            new_tree_node.parent = parent
            stack.append(new_tree_node)

        return root


class BestFitStrategy(TreeBuildingStrategy):
    """Concrete implementation of a best-fit tree building strategy."""

    def __init__(self, auto_merge_isolated_node: bool = False):
        """
        Initialize the BestFitStrategy with specific parameters.

        Args:
            another_param (str): A parameter specific to the best-fit strategy.
        """
        self.auto_merge_isolated_node = auto_merge_isolated_node
        if auto_merge_isolated_node:
            raise NotImplementedError(
                "Auto-merge isolated nodes is not yet implemented."
            )  # TODO: Implement it

    def build_tree(self, chain: List[ChainNode]) -> TreeNode:
        """
        Build a tree structure with fault tolerance, attempting to place irregular nodes in the best position.

        Args:
            chain (List[ChainNode]): List of ChainNodes.

        Returns:
            TreeNode: The root of the constructed tree using best-fit rules.
        """

        def _find_best_parent(node: TreeNode, level_seq: List[int]) -> TreeNode:
            """Find the best parent node, returning the node with the most matching sequence."""
            if not level_seq:
                return node

            from collections import deque

            queue = deque([node])
            best_match = node
            best_match_length = 0

            while queue:
                current = queue.popleft()

                # Check if the current node is a better parent match
                if (
                    current.level_seq
                    and len(current.level_seq) < len(level_seq)
                    and current.level_seq == level_seq[: len(current.level_seq)]
                    and len(current.level_seq) >= best_match_length
                ):
                    best_match = current
                    best_match_length = len(current.level_seq)

                # Continue searching child nodes
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

            # Find the best parent node and add the new node
            parent = _find_best_parent(root, node.level_seq)
            new_tree_node.parent = parent
            parent.children.append(new_tree_node)

        return root


class TreeBuilder:
    """Class that builds a tree using a specified strategy."""

    def __init__(self, strategy: Optional[TreeBuildingStrategy] = None):
        """
        Initialize the TreeBuilder with a specified strategy.

        Args:
            strategy (TreeBuildingStrategy): An instance of a strategy to build the tree. None defaults to StrictStrategy.
        """
        if strategy is None:
            strategy = BestFitStrategy()  # default strategy

        self.strategy = strategy

    def build_tree(self, chain: List[ChainNode]) -> TreeNode:
        """
        Build a tree from a list of ChainNodes using the specified strategy.

        Args:
            chain (List[ChainNode]): List of ChainNodes.

        Returns:
            TreeNode: The root of the constructed tree.
        """
        return self.strategy.build_tree(chain)


class TreeExporter:
    @staticmethod
    def export_chain(chain: List[ChainNode]) -> str:
        """
        Export the chain as a string.

        Args:
            chain (List[ChainNode]): List of ChainNodes.

        Returns:
            str: Formatted string of the chain.
        """
        return "\n".join(f"LEVEL-{n.level_seq}: {n.title}" for n in chain)

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
