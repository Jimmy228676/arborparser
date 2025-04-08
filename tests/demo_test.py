from arborparser import TreeBuilder, TreeExporter
from arborparser import ChainParser
from arborparser import (
    NUMERIC_DOT_PATTERN_BUILDER,
    ENGLISH_CHAPTER_PATTERN_BUILDER,
)


if __name__ == "__main__":
    # Sample data (updated to use English chapter format)
    test_text = """
    Chapter 1 Animals
    1.1 Mammals
    1.1.1 Primates
    1.2 Reptiles
    1.3.3 Snakes # wrong
    1.2.2 Crocodiles # hopefully inserted to the upper nearest 1.2
    1.2 wrong 1.2 # create a new level as a child of 1
    1.2.3 Lizards
    1.3 Birds
    1.3.1 Parrots
    1.3.2 Pigeons
    Chapter 2 Plants
    2.1 Angiosperms
    2.1.1 Dicotyledons
    2.1.2 Monocotyledons
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
