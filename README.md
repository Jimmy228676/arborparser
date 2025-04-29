# ArborParser

ArborParser is a powerful Python library designed to parse structured text documents and convert them into a tree representation based on hierarchical headings. It intelligently handles various numbering schemes and document inconsistencies, making it ideal for processing outlines, reports, technical documentation, legal texts, and more.

## Features

*   **Chain Parsing:** Converts text into a linear sequence (`ChainNode` list) representing the document's hierarchical structure.
*   **Flexible Pattern Definition:** Define custom parsing patterns using regular expressions and specific number converters (Arabic, Roman, Chinese, Letters, Circled).
*   **Built-in Patterns:** Provides ready-to-use patterns for common heading styles (`1.2.3`, `Chapter 1`, `第一章`, etc.).
*   **Robust Tree Building:** Transforms the linear chain into a true hierarchical `TreeNode` structure.
*   **Automatic Error Correction:** Includes an `AutoPruneStrategy` to intelligently handle skipped heading levels or lines mistakenly identified as headings.
*   **Node Manipulation:** Allows merging content between nodes (`concat_node`) for flexibility in handling non-heading text or correcting parsing errors.
*   **Reversible Transformation:** Preserves original text, enabling full document reconstruction from the tree (`tree.get_full_content()`).
*   **Export Capabilities:** Outputs the parsed structure in various formats (e.g., human-readable tree view).

**Example Transformation:**

**Original Text**
```text
Chapter 1 Animals
1.1 Mammals
1.1.1 Primates
1.2 Reptiles
Chapter 2 Plants
2.1 Angiosperms
```

**Chain Structure (Intermediate)**
```
LEVEL-[]: ROOT
LEVEL-[1]: Animals
LEVEL-[1, 1]: Mammals
LEVEL-[1, 1, 1]: Primates
LEVEL-[1, 2]: Reptiles
LEVEL-[2]: Plants
LEVEL-[2, 1]: Angiosperms
```

**Tree Structure (Final)**
```
ROOT
├─ Chapter 1 Animals
│   ├─ 1.1 Mammals
│   │   └─ 1.1.1 Primates
│   └─ 1.2 Reptiles
└─ Chapter 2 Plants
    └─ 2.1 Angiosperms
```

## Installation

```bash
pip install arborparser
```

## Basic Usage

```python
from arborparser.chain import ChainParser
from arborparser.tree import TreeBuilder, TreeExporter, AutoPruneStrategy
from arborparser.pattern import ENGLISH_CHAPTER_PATTERN_BUILDER, NUMERIC_DOT_PATTERN_BUILDER

test_text = """
Chapter 1 Animals
1.1 Mammals
1.1.1 Primates
1.2 Reptiles
Chapter 2 Plants
2.1 Angiosperms
"""

# 1. Define parsing patterns
patterns = [
    ENGLISH_CHAPTER_PATTERN_BUILDER.build(),
    NUMERIC_DOT_PATTERN_BUILDER.build(),
]

# 2. Parse text to chain
parser = ChainParser(patterns)
chain = parser.parse_to_chain(test_text)

# 3. Build tree (using AutoPrune for robustness)
builder = TreeBuilder(strategy=AutoPruneStrategy())
tree = builder.build_tree(chain)

# 4. Print the structured tree
print(TreeExporter.export_tree(tree))
```

## Key Features in Detail

### Built-in & Custom Patterns

Quickly parse common formats using builders like `NUMERIC_DOT_PATTERN_BUILDER`, `CHINESE_CHAPTER_PATTERN_BUILDER`, etc., or define your own using `PatternBuilder` for full control over prefixes, suffixes, number types, and separators.

```python
# Example: Match "Section A.", "Section B."
letter_section_pattern = PatternBuilder(
    prefix_regex=r"Section\s",
    number_type=NumberType.LETTER,
    suffix_regex=r"\."
).build()
```

### Automatic Error Correction (AutoPruneStrategy)

Documents aren't always perfect. `AutoPruneStrategy` (the default for `TreeBuilder`) handles common issues like skipped heading numbers (e.g., `1.1` followed by `1.3`) and prunes lines incorrectly matched as headings, ensuring a more robust parsing process compared to the `StrictStrategy`.

Okay, here is a dedicated section explaining `AutoPruneStrategy` using the provided example, formatted for a README without using Python code blocks for the illustration:

---

### Automatic Error Correction (AutoPruneStrategy)

Real-world documents often contain structural inconsistencies that can challenge parsers. Common issues include:

*   **Skipped Heading Levels:** Authors might jump from `1.1` directly to `1.3`, omitting `1.2`.
*   **False Positives:** Regular text lines might accidentally match a heading pattern (e.g., a sentence mentioning "section 1.1").

The `AutoPruneStrategy` (used by default in `TreeBuilder`) is designed to handle these imperfections gracefully. It uses heuristics to identify likely errors and prune the intermediate structure, resulting in a more accurate final tree.

**Example: Handling Imperfections**

Consider the following text with a missing section (`1.2`) and a line of text containing `1.1` which could be mistaken for a heading:

**Input Text:**

```text
Chapter 1 The Foundation
    Introductory content for the first chapter.

1.1 Core Concepts
    Explanation of the fundamental ideas.
    This section lays the groundwork.

# NOTE: Heading '1.2 Intermediate Concepts' is MISSING here.

1.3 Advanced Topics
    Discussing more complex subjects. We build upon the ideas from section
    1.1. This section is more advanced and goes into more detail.
    # NOTE: The '1.1.' here is text, not a heading.

Chapter 2 Building Blocks
    Content for the second chapter.

2.1 Component A
    Details about the first component.

2.2 Component B
    Details about the second component. End of document.
```

**Intermediate Chain (Before Pruning):**

A naive parsing step might initially produce a chain like this, including the misidentified heading:

```
LEVEL-[]: ROOT
LEVEL-[1]: The Foundation
LEVEL-[1, 1]: Core Concepts
LEVEL-[1, 3]: Advanced Topics
LEVEL-[1, 1]: This section is more advanced and goes into more detail.  <-- POTENTIAL FALSE POSITIVE
LEVEL-[2]: Building Blocks
LEVEL-[2, 1]: Component A
LEVEL-[2, 2]: Component B
```

**How AutoPrune Works:**

When building the tree, `AutoPruneStrategy` analyzes the sequence:

1.  It recognizes that `LEVEL-[1, 3]` can logically follow `LEVEL-[1, 1]` even if `[1, 2]` is missing (sibling jump).
2.  It sees the subsequent `LEVEL-[1, 1]` node ("This section...") followed by a completely different hierarchy (`LEVEL-[2]`). This discontinuity strongly suggests the second `LEVEL-[1, 1]` node was a false positive.
3.  The strategy "prunes" the misidentified node, effectively merging its content back into the preceding valid node (`LEVEL-[1, 3]` in this case, depending on implementation details of content association).

**Final Tree Structure (After AutoPrune):**

The resulting tree correctly reflects the intended document structure:

```
ROOT
├─ Chapter 1 The Foundation
│   ├─ 1.1 Core Concepts
│   └─ 1.3 Advanced Topics  # Correctly handles the jump & ignored false positive
└─ Chapter 2 Building Blocks
    ├─ 2.1 Component A
    └─ 2.2 Component B
```

### Node Operations & Reversibility

ArborParser works with `ChainNode` (linear sequence) and `TreeNode` (hierarchical tree) objects. Both inherit from `BaseNode`, which stores `level_seq`, `title`, and the original `content` string.

*   **Concatenating Content:** You can merge the content of one node into another. This is useful internally for associating non-heading text with its preceding heading or for merging nodes during error correction.
    ```python
    # Append node B's content to node A
    node_a.concat_node(node_b)
    ```

*   **Merging Children:** A parent node can absorb the content of all its descendants.
    ```python
    # Make node_a contain its own content plus all content from its children/grandchildren...
    node_a.merge_all_children()
    ```

*   **Reconstructing Original Text:** Because each node retains its original text chunk (`content`), you can reconstruct the *entire* original document from the root `TreeNode`. This verifies parsing integrity and allows regeneration after modification.
    ```python
    # Get the full text back from the parsed tree structure
    reconstructed_text = root_node.get_full_content()
    assert reconstructed_text == original_text # Verification
    ```

## Potential Use Cases

*   Documentation Parsing
*   Legal Document Analysis (Laws, Contracts)
*   Outline Processing & Conversion
*   Report Structuring & Analysis
*   Content Management System Import
*   Data Extraction from Structured Text
*   Format Conversion (e.g., Text to HTML/XML preserving structure)
*   Better Chunking Strategies for RAG

## Contributing

Contributions (pull requests, issues) are welcome!

## License

MIT License.
