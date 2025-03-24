# ArborParser

ArborParser is a powerful Python library designed to parse structured text documents and convert them into a tree representation based on hierarchical headings. This library is particularly useful for processing documents with nested headings, such as outlines, reports, or technical documentation.

## Features

- **Chain Parsing**: Convert text into a sequence of chain nodes that represent the hierarchical structure of the document.
- **Tree Building**: Transform chain nodes into a tree structure, maintaining hierarchical relationships.
- **Pattern Customization**: Define custom parsing patterns using regular expressions to fit different document formats.
- **Export Capabilities**: Output the parsed structure in various formats, including plain text and JSON.

## Example

Given a text document with headings, ArborParser can parse and structure it as follows:

### Original Text
```
Chapter 1 Animals
1.1 Mammals
1.1.1 Primates
1.2 Reptiles
1.2.2 Crocodiles
1.3 Birds
1.3.1 Parrots
1.3.2 Pigeons
Chapter 2 Plants
2.1 Angiosperms
2.1.1 Dicotyledons
2.1.2 Monocotyledons
```

### Chain Structure

```
LEVEL-[1]: Animals
LEVEL-[1, 1]: Mammals
LEVEL-[1, 1, 1]: Primates
LEVEL-[1, 2]: Reptiles
LEVEL-[1, 2, 2]: Crocodiles
LEVEL-[1, 3]: Birds
LEVEL-[1, 3, 1]: Parrots
LEVEL-[1, 3, 2]: Pigeons
LEVEL-[2]: Plants
LEVEL-[2, 1]: Angiosperms
LEVEL-[2, 1, 1]: Dicotyledons
LEVEL-[2, 1, 2]: Monocotyledons
```

### Tree Structure

```
ROOT
├─ Chapter 1 Animals
│   ├─ 1.1 Mammals
│   │   └─ 1.1.1 Primates
│   ├─ 1.2 Reptiles
│   │   └─ 1.2.2 Crocodiles
│   └─ 1.3 Birds
│       ├─ 1.3.1 Parrots
│       └─ 1.3.2 Pigeons
└─ Chapter 2 Plants
    └─ 2.1 Angiosperms
        ├─ 2.1.1 Dicotyledons
        └─ 2.1.2 Monocotyledons
```

## Installation

To install ArborParser, you can use `pip`:

```shell
pip install arborparser
```

## Usage

Here's a basic example of how to use ArborParser:

```python
from arborparser.tree import TreeBuilder, TreeExporter
from arborparser.chain import ChainParser
from arborparser.pattern import (
    ENGLISH_CHAPTER_PATTERN_BUILDER,
    NUMERIC_DOT_PATTERN_BUILDER,
)

test_text = """
Chapter 1 Animals
1.1 Mammals
1.1.1 Primates
1.2 Reptiles
1.2.2 Crocodiles
1.3 Birds
1.3.1 Parrots
1.3.2 Pigeons
Chapter 2 Plants
2.1 Angiosperms
2.1.1 Dicotyledons
2.1.2 Monocotyledons
"""

# Define your parsing patterns
patterns = [
    ENGLISH_CHAPTER_PATTERN_BUILDER.build(),
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
