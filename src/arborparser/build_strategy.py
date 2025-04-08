from abc import ABC, abstractmethod
from typing import List, Deque
from arborparser.node import ChainNode, TreeNode, BaseNode
from collections import deque


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


def create_root() -> TreeNode:
    """Create a root node for the tree."""
    return TreeNode(level_seq=[], level_text="", title="ROOT")


def get_prefix(level_seq: List[int]) -> List[int]:
    if len(level_seq) == 0:
        return []
    else:
        return level_seq[:-1]


def get_last_level(level_seq: List[int]):
    if len(level_seq) == 0:
        return 0
    else:
        return level_seq[-1]


def is_imm_next(front_seq: List[int], back_seq: List[int]) -> bool:
    """
    Determine if two nodes are immediate siblings based on their sequences.
    There are three scenarios to consider:
    1. **Same level siblings**: If both sequences are of the same length, check if they share the same prefix
       and the last level of the front sequence is immediately followed by the last level of the back sequence.
       Example: `front_seq = [1, 1, 1]` and `back_seq = [1, 1, 2]`.

    2. **Parent to child**: If the back sequence is exactly one level deeper than the front sequence, check if
       the front sequence matches the prefix of the back sequence.
       Example: `front_seq = [1, 2]` and `back_seq = [1, 2, 1]`.

    3. **Different level siblings**: If the front sequence is deeper than the back sequence, truncate the front
       sequence until they are of the same level, and then check if they are immediate siblings.
       Example: `front_seq = [1, 1, 2, 3]` and `back_seq = [1, 2]`.
    """

    if len(front_seq) == len(back_seq):  # eg: 1.1.1 -> 1.1.3
        return (get_prefix(front_seq) == get_prefix(back_seq)) and (
            get_last_level(front_seq) + 1 == get_last_level(back_seq)
        )
    elif len(front_seq) + 1 == len(back_seq):  # eg: 1.2 -> 1.2.1
        return front_seq == get_prefix(back_seq)
    elif len(front_seq) > len(back_seq):  # eg: 1.1.2.3 -> 1.2
        front_seq_prefix = front_seq
        while len(front_seq_prefix) > len(back_seq):
            front_seq_prefix = get_prefix(front_seq_prefix)
        return (get_prefix(front_seq_prefix) == get_prefix(back_seq)) and (
            get_last_level(front_seq_prefix) + 1 == get_last_level(back_seq)
        )
    else:
        return False


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
            new_tree_node = TreeNode.from_chain_node(node)

            # Logic to find appropriate parent node
            parent = root  # Default parent node is root
            while stack:
                candidate = stack[-1]
                if _is_child(candidate.level_seq, new_tree_node.level_seq):
                    parent = candidate
                    break
                stack.pop()

            parent.add_child(new_tree_node)
            stack.append(new_tree_node)

        return root


class AutoPruneStrategy(TreeBuildingStrategy):
    """Concrete implementation of an auto-prune tree building strategy."""

    def build_tree(self, chain: List[ChainNode]) -> TreeNode:
        """
        Convert chain nodes to a tree structure using an auto-prune strategy.

        Args:
            chain (List[ChainNode]): List of ChainNodes.
        Returns:
            TreeNode: The root of the constructed tree using auto-prune rules.
        """

        root = create_root()
        current_branch: List[TreeNode] = [root]
        not_imm_node_queue: Deque[ChainNode] = deque()
        current_node = root

        def add_node_and_update_current_branch(node: TreeNode) -> None:
            """Find the parent node of a given node and truncate the parent stack."""
            nonlocal current_branch
            node_prefix = node.level_seq
            for index in reversed(range(len(current_branch))):
                parent = current_branch[index]
                while len(parent.level_seq) < len(node_prefix):
                    node_prefix = get_prefix(node_prefix)
                if parent.level_seq == node_prefix:
                    del current_branch[index + 1 :]
                    current_branch.append(node)
                    parent.add_child(node)
                    return
            assert False, "Parent node not found"

        def add_node_to_tree(node: ChainNode) -> None:
            """Add a node to the tree."""
            nonlocal current_node
            new_tree_node = TreeNode.from_chain_node(node)
            add_node_and_update_current_branch(new_tree_node)
            current_node = new_tree_node

        def concat_one_not_imm_node_to_current_node() -> None:
            """Concatenate one node from not_imm_node_stack to current_node."""
            nonlocal current_node, not_imm_node_queue
            not_imm_node = not_imm_node_queue.popleft()
            current_node.concat_node(not_imm_node)

        def is_all_not_imm_nodes_siblings() -> bool:
            """Check if all nodes in not_imm_node_stack are siblings."""
            nonlocal not_imm_node_queue
            if len(not_imm_node_queue) < 2:
                return True
            for i in range(len(not_imm_node_queue) - 1):
                if not is_imm_next(
                    not_imm_node_queue[i].level_seq, not_imm_node_queue[i + 1].level_seq
                ):
                    return False
            return True

        for node in chain:
            # add node to tree if it is immediate next to current_node
            if is_imm_next(current_node.level_seq, node.level_seq):
                # merge not_imm_node_stack into current_node
                while not_imm_node_queue:
                    concat_one_not_imm_node_to_current_node()
                add_node_to_tree(node)
            else:
                not_imm_node_queue.append(node)

            assert len(not_imm_node_queue) <= 3, "Too many nodes in not_imm_node_stack"
            # if there are three nodes in not_imm_node_stack, check if they are siblings
            if len(not_imm_node_queue) == 3:
                if is_all_not_imm_nodes_siblings():
                    while not_imm_node_queue:
                        add_node_to_tree(not_imm_node_queue.popleft())
                else:
                    concat_one_not_imm_node_to_current_node()

        while not_imm_node_queue:
            add_node_to_tree(not_imm_node_queue.popleft())

        return root
