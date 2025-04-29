from arborparser.chain import ChainParser
from arborparser.tree import TreeBuilder, TreeExporter, AutoPruneStrategy
from arborparser.pattern import (
    CHINESE_CHAPTER_PATTERN_BUILDER,
    ENGLISH_CHAPTER_PATTERN_BUILDER,
    NUMERIC_DOT_PATTERN_BUILDER,
    ROMAN_PATTERN_BUILDER,
    CIRCLED_PATTERN_BUILDER,
    PatternBuilder,
    NumberType,
)

chinese_text = """
第一章 动物
1.1 哺乳动物
1.1.1 灵长类
1.2 爬行动物
第二章 植物
2.1 被子植物
"""

english_text = """
Chapter 1 Animals
1.1 Mammals
1.1.1 Primates
1.2 Reptiles
Chapter 2 Plants
2.1 Angiosperms
"""

custom_text = """
第I章 自然
A-A. 第一部分
A-B. 场景一
第II章 科学
(2-1) 细节
"""


patterns = [
    CHINESE_CHAPTER_PATTERN_BUILDER.build(),
    ENGLISH_CHAPTER_PATTERN_BUILDER.build(),
    NUMERIC_DOT_PATTERN_BUILDER.build(),
]

print("Chinese text parsing:")
parser = ChainParser(patterns)
chain = parser.parse_to_chain(chinese_text)
builder = TreeBuilder(strategy=AutoPruneStrategy())
tree = builder.build_tree(chain)
print(TreeExporter.export_tree(tree))
print("\n")

print("English text parsing:")
parser = ChainParser(patterns)
chain = parser.parse_to_chain(english_text)
builder = TreeBuilder(strategy=AutoPruneStrategy())
tree = builder.build_tree(chain)
print(TreeExporter.export_tree(tree))
print("\n")

# define custom patterns
custom_patterns = [
    PatternBuilder(
        prefix_regex=r"第", number_type=NumberType.ROMAN, suffix_regex=r"章"
    ).build(),
    PatternBuilder(
        prefix_regex=r"",
        number_type=NumberType.LETTER,
        suffix_regex=r"\.",
        separator="-",
    ).build(),
    NUMERIC_DOT_PATTERN_BUILDER.build(),
    PatternBuilder(
        prefix_regex=r"\(",
        number_type=NumberType.ARABIC,
        suffix_regex=r"\)",
        separator="-",
    ).build(),
]

print("Custom text parsing：")
parser = ChainParser(custom_patterns)
chain = parser.parse_to_chain(custom_text)
builder = TreeBuilder(strategy=AutoPruneStrategy())
tree = builder.build_tree(chain)
print(TreeExporter.export_tree(tree))
