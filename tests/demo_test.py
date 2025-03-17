from arborparser.tree import TreeBuilder, TreeExporter
from arborparser.chain import ChainParser
from arborparser.pattern import (
    CHINESE_CHAPTER_PATTERN_BUILDER,
    NUMERIC_DOT_PATTERN_BUILDER,
)

if __name__ == "__main__":
    # Sample data
    test_text = """
    第1章 动物
    1.1 哺乳类
    1.1.1 灵长类
    1.2 爬行类
    1.3.3 蛇 # wrong
    1.2.2 鳄鱼 # hopefully inserted to the upper nearest 1.2
    1.2 wrong 1.2 # create a new level as a child of 1
    1.3 鸟类
    1.3.1 鹦鹉
    1.3.2 鸽子
    第2章 植物
    2.1 被子植物
    2.1.1 双子叶植物
    2.1.2 单子叶植物
    """

    # Configure parsing rules
    patterns = [
        CHINESE_CHAPTER_PATTERN_BUILDER.build(),
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
    # print(TreeExporter.export_to_json(tree, concat_title_in_content=True))
