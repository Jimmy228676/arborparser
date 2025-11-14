from abc import ABC, abstractmethod
from typing import List, Deque, Union, Sequence, Optional, cast
from arborparser.node import ChainNode, TreeNode, BaseNode
from collections import deque


class TreeBuildingStrategy(ABC):
    """Abstract base class for tree building strategies."""

    @abstractmethod
    def build_tree(
        self, chain: Union[List[ChainNode], List[List[ChainNode]]]
    ) -> TreeNode:
        """
        Build a tree from a list (or list of lists) of ChainNodes.

        Args:
            chain: Either single-choice ChainNodes or multi-candidate rows.

        Returns:
            TreeNode: The root of the constructed tree.
        """
        pass


def is_root(node: BaseNode) -> bool:
    """Check if a node is the root of a tree."""
    return len(node.level_seq) == 0


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
            get_last_level(front_seq) < get_last_level(back_seq)
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


def _ensure_multi_chain(
    chain: Union[List[ChainNode], List[List[ChainNode]]]
) -> List[List[ChainNode]]:
    if not chain:
        raise ValueError("Chain cannot be empty")

    first = chain[0]
    if isinstance(first, ChainNode):
        return [[node] for node in chain]  # type: ignore[arg-type]
    return cast(List[List[ChainNode]], chain)


def _select_by_priority(candidates: Sequence[ChainNode]) -> ChainNode:
    if not candidates:
        raise ValueError("Expected at least one ChainNode candidate")
    best = candidates[0]
    for candidate in candidates[1:]:
        if candidate.pattern_priority < best.pattern_priority:
            best = candidate
    return best


class StrictStrategy(TreeBuildingStrategy):
    """Concrete implementation of a strict tree building strategy."""

    def build_tree(
        self, chain: Union[List[ChainNode], List[List[ChainNode]]]
    ) -> TreeNode:
        """
        Convert chain nodes to a tree structure using a strict strategy.

        Args:
            chain: ChainNodes or multi-candidate rows.

        Returns:
            TreeNode: The root of the constructed tree using strict rules.
        """

        def _is_child(parent_seq: List[int], child_seq: List[int]) -> bool:
            """Determine if child is a direct child of parent."""
            return (
                len(child_seq) == len(parent_seq) + 1 and child_seq[:-1] == parent_seq
            )

        flattened_chain = self._flatten_chain(chain)

        if not is_root(flattened_chain[0]):
            raise ValueError("First node must be root")

        root = TreeNode.from_chain_node(flattened_chain[0])
        stack = [root]  # Current hierarchy path stack

        for node in flattened_chain[1:]:
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

    def _flatten_chain(
        self, chain: Union[List[ChainNode], List[List[ChainNode]]]
    ) -> List[ChainNode]:
        multi_chain = _ensure_multi_chain(chain)
        selected: List[ChainNode] = []
        for candidates in multi_chain:
            if not candidates:
                continue
            selected.append(_select_by_priority(candidates))
        if not selected:
            raise ValueError("Chain cannot be empty after selection")
        return selected


class AutoPruneStrategy(TreeBuildingStrategy):
    """Concrete implementation of an auto-prune tree building strategy."""

    def build_tree(
        self, chain: Union[List[ChainNode], List[List[ChainNode]]]
    ) -> TreeNode:
        """
        Convert chain nodes to a tree structure using an auto-prune strategy.

        Args:
            chain: ChainNodes or multi-candidate rows.
        Returns:
            TreeNode: The root of the constructed tree using auto-prune rules.
        """

        multi_chain = _ensure_multi_chain(chain)
        root_candidate = _select_by_priority(multi_chain[0])

        if not is_root(root_candidate):
            raise ValueError("First node must be root")

        root = TreeNode.from_chain_node(root_candidate)
        current_branch: List[TreeNode] = [root]
        not_imm_node_queue: Deque[List[ChainNode]] = deque()
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
            """Concatenate one candidate line from not_imm_node_queue to current_node."""
            nonlocal current_node, not_imm_node_queue
            candidates = not_imm_node_queue.popleft()
            if not candidates:
                return
            current_node.concat_node(_select_by_priority(candidates))

        for candidates in multi_chain[1:]:
            if not candidates:
                continue

            immediate_node = self._select_immediate_candidate(current_node, candidates)

            if immediate_node:
                # merge queued nodes deemed as noise before attaching the new node
                while not_imm_node_queue:
                    concat_one_not_imm_node_to_current_node()
                add_node_to_tree(immediate_node)
            else:
                not_imm_node_queue.append(candidates)

            assert len(not_imm_node_queue) <= 3, "Too many nodes in not_imm_node_stack"
            if len(not_imm_node_queue) == 3:
                contiguous = self._find_contiguous_sequence(list(not_imm_node_queue))
                if contiguous:
                    not_imm_node_queue.clear()
                    for node in contiguous:
                        add_node_to_tree(node)
                else:
                    concat_one_not_imm_node_to_current_node()

        while not_imm_node_queue:
            concat_one_not_imm_node_to_current_node()

        return root

    @staticmethod
    def _select_immediate_candidate(
        prev_node: BaseNode, candidates: Sequence[ChainNode]
    ) -> Optional[ChainNode]:
        immediate_candidates = [
            node for node in candidates if is_imm_next(prev_node.level_seq, node.level_seq)
        ]
        if not immediate_candidates:
            return None
        return _select_by_priority(immediate_candidates)

    @staticmethod
    def _find_contiguous_sequence(
        candidate_groups: Sequence[Sequence[ChainNode]],
    ) -> Optional[List[ChainNode]]:
        if not candidate_groups:
            return None

        search_queue = deque([(0, None, [])])  # (group_index, prev_node, path)

        while search_queue:
            index, prev_node, path = search_queue.popleft()
            if index == len(candidate_groups):
                return path

            for candidate in candidate_groups[index]:
                if prev_node is None or is_imm_next(prev_node.level_seq, candidate.level_seq):
                    search_queue.append((index + 1, candidate, path + [candidate]))

        return None
