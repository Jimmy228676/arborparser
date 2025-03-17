# ArborParser

ArborParser is a powerful Python library designed to parse structured text documents and convert them into a tree representation based on hierarchical headings. This library is particularly useful for processing documents with nested headings, such as outlines, reports, or technical documentation.

## Features

- **Chain Parsing**: Convert text into a sequence of chain nodes that represent the hierarchical structure of the document.
- **Tree Building**: Transform chain nodes into a tree structure, maintaining hierarchical relationships.
- **Pattern Customization**: Define custom parsing patterns using regular expressions to fit different document formats.
- **Export Capabilities**: Output the parsed structure in various formats, including plain text and JSON.

## Example

Given a text document with headings, ArborParser can parse and structure it as follows:

### Chain Structure

```
LEVEL-[1]: 动物
LEVEL-[1, 1]: 哺乳类
LEVEL-[1, 1, 1]: 灵长类
LEVEL-[1, 2]: 爬行类
LEVEL-[1, 3, 3]: 蛇 # wrong
LEVEL-[1, 2, 2]: 鳄鱼 # hopefully inserted to the upper nearest 1.2
LEVEL-[1, 2]: wrong 1.2 # create a new level as a child of 1
LEVEL-[1, 3]: 鸟类
LEVEL-[1, 3, 1]: 鹦鹉
LEVEL-[1, 3, 2]: 鸽子
LEVEL-[2]: 植物
LEVEL-[2, 1]: 被子植物
LEVEL-[2, 1, 1]: 双子叶植物
LEVEL-[2, 1, 2]: 单子叶植物
```

### Tree Structure

```
ROOT
├─ 第1章 动物
│   ├─ 1.1 哺乳类
│   │   └─ 1.1.1 灵长类
│   ├─ 1.2 爬行类
│   │   └─ 1.2.2 鳄鱼 # hopefully inserted to the upper nearest 1.2
│   ├─ 1.3.3 蛇 # wrong
│   ├─ 1.2 wrong 1.2 # create a new level as a child of 1
│   └─ 1.3 鸟类
│       ├─ 1.3.1 鹦鹉
│       └─ 1.3.2 鸽子
└─ 第2章 植物
    └─ 2.1 被子植物
        ├─ 2.1.1 双子叶植物
        └─ 2.1.2 单子叶植物
```

## Installation

To install ArborParser, you can use `pip`:

```bash
pip install arborparser
```

## Usage

Here's a basic example of how to use ArborParser:

```python
from arborparser.tree import TreeBuilder, TreeExporter
from arborparser.chain import ChainParser
from arborparser.pattern import (
    CHINESE_CHAPTER_PATTERN_BUILDER,
    NUMERIC_DOT_PATTERN_BUILDER,
)

# Define your parsing patterns
patterns = [
    CHINESE_CHAPTER_PATTERN_BUILDER.build(),
    NUMERIC_DOT_PATTERN_BUILDER.build(),
]

# Parse the text
parser = ChainParser(patterns)
chain = parser.parse_to_chain(test_text)

# Build and export the tree
builder = TreeBuilder()
tree = builder.build_tree(chain)
print(TreeExporter.export_tree(tree))
```

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue.

## License

This project is licensed under the MIT License.