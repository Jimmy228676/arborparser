# arborparser imports
from arborparser.tree import TreeBuilder, TreeNode
from arborparser.chain import ChainParser, LevelPattern
from arborparser.pattern import (
    CHINESE_CHAPTER_PATTERN_BUILDER,
    NUMERIC_DOT_PATTERN_BUILDER,
    ENGLISH_CHAPTER_PATTERN_BUILDER,
)
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.schema import TextNode
from typing import Tuple, Dict, Any, List


class ArborParserNodeParser:
    """Custom parser for document parsing and chunking using ArborParser."""

    def __init__(
        self,
        chunk_size: int = 1024,
        chunk_overlap: int = 80,
        merge_threshold: int = 5000,
        is_merge_small_node: bool = True,
        level_patterns: List[LevelPattern] | None = None,
    ):
        """
        Initialize the ArborParserNodeParser with the given parameters.

        Args:
            chunk_size: The size of the chunks to split the text into.
            chunk_overlap: The overlap between chunks.
            merge_threshold: The threshold for merging small nodes.
            is_merge_small_node: Whether to merge small nodes.
            level_patterns: The level patterns to use for the parser.
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.merge_threshold = merge_threshold
        self.is_merge_small_node = is_merge_small_node
        self.sentence_splitter = SentenceSplitter(
            chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap
        )

        # Define chapter patterns
        self.patterns = None
        if not level_patterns:
            chinese_chapter_pattern = CHINESE_CHAPTER_PATTERN_BUILDER.modify(
                prefix_regex=r"[\#\s]*第?",  # "第" means "Chapter" or "Section"
            ).build()

            english_chapter_pattern = ENGLISH_CHAPTER_PATTERN_BUILDER.modify(
                prefix_regex=r"[\#\s]*Chapter\s",
            ).build()

            sector_pattern = NUMERIC_DOT_PATTERN_BUILDER.modify(
                prefix_regex=r"[\#\s]*",
                suffix_regex=r"[\.\s]*",
                min_level=2,
            ).build()

            self.patterns = [
                chinese_chapter_pattern,
                english_chapter_pattern,
                sector_pattern,
            ]
        else:
            self.patterns = level_patterns

    def merge_deep_nodes(self, node: TreeNode) -> None:
        """
        Recursively merge nodes to make each node's length as close to the threshold as possible.

        Args:
            node: The node to process.
        """
        # First, recursively process all child nodes
        for child in node.children:
            self.merge_deep_nodes(child)

        def mergable(
            node1: TreeNode, node2: TreeNode, is_pre_node_parent: bool
        ) -> bool:
            if (not is_pre_node_parent) and len(node1.children) > 0:
                return False
            if len(node2.children) > 0:
                return False
            return len(node1.content) + len(node2.content) < self.merge_threshold

        idx = -1  # -1 indicates the parent node
        while idx < len(node.children) - 1:
            is_pre_node_parent = idx == -1
            if is_pre_node_parent:
                pre_node = node
            else:
                pre_node = node.children[idx]
            next_node = node.children[idx + 1]
            if mergable(pre_node, next_node, is_pre_node_parent):
                pre_node.concat_node(next_node)
                node.children.pop(idx + 1)
            else:
                idx += 1

    def split_node_content(self, node: TreeNode) -> List[str]:
        """
        Split the node content into chunks using SentenceSplitter.

        Args:
            node: The node to split.

        Returns:
            A list of text chunks.
        """
        if node.content:
            return self.sentence_splitter.split_text(node.content)
        return []

    def collect_chunks_with_path(
        self, node: TreeNode, title_path: List[str] = None
    ) -> List[Tuple[str, Dict[str, Any]]]:
        """
        Recursively collect chunks from all nodes in the tree, along with their title paths.

        Args:
            node: The current node being processed.
            title_path: The title path of the current node.

        Returns:
            A list of tuples, each containing a text chunk and its metadata.
        """
        if title_path is None:
            title_path = []

        # Update the title path for the current node
        current_path = title_path.copy()
        if node.title.strip():
            current_path.append(node.title.strip())

        # Chunks for the current node
        chunks = []
        if node.content:
            text_chunks = self.split_node_content(node)
            # Add title path metadata to each chunk
            for chunk in text_chunks:
                chunks.append(
                    (
                        chunk,
                        {
                            "title_path": (
                                " > ".join(current_path) if current_path else "Root"
                            ),
                        },
                    )
                )

        # Recursively collect chunks from all child nodes
        for child in node.children:
            chunks.extend(self.collect_chunks_with_path(child, current_path))

        return chunks

    def parse_text(self, text: str) -> List[Tuple[str, Dict[str, Any]]]:
        """
        Parse the text and return a list of chunks with their metadata.

        Args:
            text: The text to parse.

        Returns:
            A list of tuples, each containing a text chunk and its metadata.
        """
        # Parse the text structure
        parser = ChainParser(self.patterns)
        chain = parser.parse_to_chain(text)

        # Build the tree
        builder = TreeBuilder()
        tree = builder.build_tree(chain)

        # Merge small nodes
        if self.is_merge_small_node:
            pre_content = tree.get_full_content()
            self.merge_deep_nodes(tree)
            post_content = tree.get_full_content()
            # Verify that the merging process did not lose content
            assert pre_content == post_content

        # Collect all chunks and their title paths
        chunks_with_metadata = self.collect_chunks_with_path(tree)
        assert len(chunks_with_metadata) > 0

        return chunks_with_metadata

    def get_nodes_from_documents(self, documents, show_progress=False):
        """
        Get nodes from a list of documents.

        Args:
            documents: A list of documents.
            show_progress: Whether to show progress.
        Returns:
            A list of parsed TextNode nodes.
        """
        nodes = []

        for doc in documents:
            # Parse the document using ArborParser and get chunks with title paths
            chunks_with_metadata = self.parse_text(doc.text)

            # Create nodes
            for i, (chunk, title_metadata) in enumerate(chunks_with_metadata):
                node = TextNode(
                    text=chunk,
                    metadata={
                        "file_name": doc.metadata.get("file_name", ""),
                        "file_path": doc.metadata.get("file_path", ""),
                        "chunk_id": i,
                        "title_path": title_metadata["title_path"],
                    },
                )
                nodes.append(node)

        return nodes
