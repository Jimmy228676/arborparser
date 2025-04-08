from abc import ABC, abstractmethod
from typing import List
from arborparser.node import ChainNode, TreeNode


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

        # FIXME: root.get_full_content() should always return the original content.
        # BestFitStrategy violates this constraint.

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
