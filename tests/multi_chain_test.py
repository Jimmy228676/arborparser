from arborparser import TreeBuilder, TreeExporter
from arborparser import ChainParser
from arborparser import (
    NUMERIC_DOT_PATTERN_BUILDER,
    ENGLISH_CHAPTER_PATTERN_BUILDER,
)


if __name__ == "__main__":
    test_text = """
Chapter 2 Building Blocks
    Content for the second chapter.

2.1 A Component
    Details about the first component.

2.1.1 A details
    Details 1

2.1 .2 A details 2 [the title is corrupted due to OCR or other reasons]
    Details 2

2.2 2-Sided Materials B Component
    Details about the second component.
"""

    # Configure parsing rules
    non_strict_num_pattern = NUMERIC_DOT_PATTERN_BUILDER.modify(
        prefix_regex=r"[\#\s]*",
        suffix_regex=r"[\.\s]*",
        separator=r"[\.\s]+",
        is_sep_regex=True,
        min_level=2,
    ).build()

    patterns = [
        ENGLISH_CHAPTER_PATTERN_BUILDER.build(),  # Use the English chapter pattern
        NUMERIC_DOT_PATTERN_BUILDER.build(),  # Use the numeric dot pattern
        non_strict_num_pattern,
    ]

    # Parsing process
    parser = ChainParser(patterns)
    chain = parser.parse_to_multi_chain(test_text)

    print("=== Chain Structure ===")
    print(TreeExporter.export_chain(chain))

    # Build the tree
    builder = TreeBuilder()
    tree = builder.build_tree(chain)

    print("\n=== Tree Structure ===")
    print(TreeExporter.export_tree(tree))
    json_result = TreeExporter.export_to_json(tree)

    assert tree.get_full_content() == test_text
