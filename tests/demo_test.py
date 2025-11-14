from arborparser import TreeBuilder, TreeExporter
from arborparser import ChainParser
from arborparser import (
    NUMERIC_DOT_PATTERN_BUILDER,
    ENGLISH_CHAPTER_PATTERN_BUILDER,
)


if __name__ == "__main__":
    test_text = """
Chapter 1 The Foundation
    Introductory content for the first chapter.

1.1 Core Concepts
    Explanation of the fundamental ideas.
    This section lays the groundwork.

# NOTE: Heading '1.2 Intermediate Concepts' is MISSING here.
# ArborParser can handle jumping from 1.1 directly to 1.3.

1.3 Advanced Topics
    Discussing more complex subjects. We build upon the ideas from section 
    1.1. This section is more advanced and goes into more detail.
    # NOTE: The '1.1' above is *part of the text content*.
    # AutoPrune Strategy will identify the discontinuity and prune this wrongly detected node.

Chapter 2 Building Blocks
    Content for the second chapter.

2.1 Component A
    Details about the first component.

2.2 Component B
    Details about the second component. End of document.
"""

    # Configure parsing rules
    patterns = [
        ENGLISH_CHAPTER_PATTERN_BUILDER.build(),  # Use the English chapter pattern
        NUMERIC_DOT_PATTERN_BUILDER.build(),
    ]

    # Parsing process
    parser = ChainParser(patterns)
    chain = parser.parse_to_chain(test_text)

    print("=== Chain Structure ===")
    print(TreeExporter.export_chain(chain))

    # Build the tree
    builder = TreeBuilder()
    tree = builder.build_tree(chain)

    print("\n=== Tree Structure ===")
    print(TreeExporter.export_tree(tree))
    json_result = TreeExporter.export_to_json(tree)
    # print(json_result)

    assert tree.get_full_content() == test_text
