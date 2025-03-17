from arborparser.tree import TreeBuilder, TreeExporter
from arborparser.chain import ChainParser
from arborparser.pattern import (
    CHINESE_CHAPTER_PATTERN_BUILDER,
    NUMERIC_DOT_PATTERN_BUILDER,
)

if __name__ == "__main__":
    # Test data
    file_name = "tests/test_data/test1.md"
    with open(file_name, "r", encoding="utf-8") as file:
        test_text = file.read()

    # Modifying chapter pattern to match specific format
    chapter_pattern = CHINESE_CHAPTER_PATTERN_BUILDER.modify(
        prefix_regex=r"[\#\s]*第?",
        suffix_regex=r"章[\.、\s]*",
    ).build()

    # Modifying sector pattern with specified prefix and suffix regex
    sector_pattern = NUMERIC_DOT_PATTERN_BUILDER.modify(
        prefix_regex=r"[\#\s]*",
        suffix_regex=r"[\.\s]*",
        min_level=2,
    ).build()

    # Configure parsing rules
    patterns = [
        chapter_pattern,
        sector_pattern,
    ]

    # Parsing process
    parser = ChainParser(patterns)
    chain = parser.parse_to_chain(test_text)

    # Export chain structure to a file
    with open("output/test1_chain.txt", "w", encoding="utf-8") as file:
        file.write(TreeExporter.export_chain(chain))

    # Build the tree
    builder = TreeBuilder()
    tree = builder.build_tree(chain)

    # Export tree structure to a file
    with open("output/test1_tree.txt", "w", encoding="utf-8") as file:
        file.write(TreeExporter.export_tree(tree))
