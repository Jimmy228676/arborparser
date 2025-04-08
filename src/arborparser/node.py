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

    @staticmethod
    def from_chain_node(chain_node: ChainNode) -> "TreeNode":
        """
        Convert a chain node to a tree node.

        Args:
            chain_node (ChainNode): The chain node to be converted.
        Returns:
            TreeNode: The converted tree node.
        """
        return TreeNode(
            level_seq=chain_node.level_seq,
            level_text=chain_node.level_text,
            title=chain_node.title,
            content=chain_node.content,
        )

    def add_child(self, child: "TreeNode") -> None:
        """
        Add a child node to the current node.

        Args:
            child (TreeNode): The child node to be added.
        """
        child.parent = self
        self.children.append(child)

    def merge_all_children(self) -> None:
        """
        Merge all children into the current node.
        """
        if not self.children:
            return

        for child in self.children:
            child.merge_all_children()
            self.concat_node(child)

        self.children = []

    def get_full_content(self) -> str:
        """
        Get the full content of the current node and all its children.
        The result should be the same as the original text, if using the strategies in this library correctly.
        """
        full_content = self.content
        for child in self.children:
            full_content += child.get_full_content()
        return full_content
