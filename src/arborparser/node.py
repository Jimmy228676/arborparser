from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class BaseNode:
    """
    Base class for all node types.

    Attributes:
        level_seq (List[int]): Sequence representing the hierarchy level (e.g., [1, 2, 3]).
        level_text (str): Text representation of the hierarchy level (e.g., "1.2.3").
        title (str): Original title text without hierarchy information.
        content (str): Associated content text, including level text and title.
    """

    level_seq: List[int]
    level_text: str = ""
    title: str = ""
    content: str = ""

    def concat_node(self, node: "BaseNode") -> None:
        """
        Concatenate another node's content onto the current node.

        Args:
            node (BaseNode): The node whose content will be concatenated.
        """
        self.content += node.content


@dataclass
class ChainNode(BaseNode):
    """
    Node in a chain structure; stores flat information only.

    Attributes:
        pattern_priority (int): Priority of the matched pattern, used for sorting.
    """

    pattern_priority: int = 0


@dataclass
class TreeNode(BaseNode):
    """
    Node in a tree structure; includes hierarchical relationships.

    Attributes:
        parent (Optional[TreeNode]): Parent node in the tree.
        children (List[TreeNode]): List of child nodes.
    """

    parent: Optional["TreeNode"] = None
    children: List["TreeNode"] = field(default_factory=list)
