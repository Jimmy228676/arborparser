# ArborParser

ArborParser 是一个功能强大的 Python 库，专门用于解析结构化文本文档并将其转换为树形结构。它能够智能处理各种编号格式和文档中的不一致问题，特别适合处理大纲、报告、技术文档和法律文本等。

## 功能特点

* **链式解析：** 将文本转换为线性序列（`ChainNode` 列表），展现文档的层次结构。
* **多候选解析：** `parse_to_multi_chain` 会保留每一行的全部标题候选，`TreeBuilder`/`TreeExporter` 可以直接处理 `List[List[ChainNode]]`。
* **灵活的模式定义：** 支持使用正则表达式和多种数字格式（阿拉伯数字、罗马数字、中文数字、字母、圈号）来定义自定义解析模式。
* **内置模式：** 内置了常见的标题格式（如 `1.2.3`、`第1章`、`第一章` 等）。
* **树形结构构建：** 将线性链转换为层次化的 `TreeNode` 结构。
* **智能纠错：** 内置 `AutoPruneStrategy`，可以智能处理标题层级跳跃或误识别为标题的文本行。
* **节点操作：** 支持合并节点内容（`concat_node`、`merge_all_children`），方便树的剪枝等后处理。
* **可逆转换：** 保留原始文本，支持从树形结构完整重建文档（`tree.get_full_content()`）。
* **导出功能：** 支持多种格式输出解析结构（如树形视图）。

**转换示例：**

**原始文本**
```text
第一章 动物
1.1 哺乳动物
1.1.1 灵长类
1.2 爬行动物
第二章 植物
2.1 被子植物
```

**链式结构（中间结果）**
```
LEVEL-[]: ROOT
LEVEL-[1]: 动物
LEVEL-[1, 1]: 哺乳动物
LEVEL-[1, 1, 1]: 灵长类
LEVEL-[1, 2]: 爬行动物
LEVEL-[2]: 植物
LEVEL-[2, 1]: 被子植物
```

**树形结构（最终结果）**
```
ROOT
├─ 第一章 动物
│   ├─ 1.1 哺乳动物
│   │   └─ 1.1.1 灵长类
│   └─ 1.2 爬行动物
└─ 第二章 植物
    └─ 2.1 被子植物
```

## 安装

```bash
pip install arborparser
```

## 基本用法

```python
from arborparser.chain import ChainParser
from arborparser.tree import TreeBuilder, TreeExporter, AutoPruneStrategy
from arborparser.pattern import CHINESE_CHAPTER_PATTERN_BUILDER, NUMERIC_DOT_PATTERN_BUILDER

test_text = """
第一章 动物
1.1 哺乳动物
1.1.1 灵长类
1.2 爬行动物
第二章 植物
2.1 被子植物
"""

# 1. 设置解析模式
patterns = [
    CHINESE_CHAPTER_PATTERN_BUILDER.build(),
    NUMERIC_DOT_PATTERN_BUILDER.build(),
]

# 2. 解析文本为链式结构
parser = ChainParser(patterns)
chain = parser.parse_to_chain(test_text)

# 3. 构建树（使用 AutoPrune 提高稳定性）
builder = TreeBuilder(strategy=AutoPruneStrategy())
tree = builder.build_tree(chain)

# 4. 输出树形结构
print(TreeExporter.export_tree(tree))
```

## 多候选链解析

当某一行可能同时匹配多个模式（或一个模式的 converter 返回多条层级路径）时，可以使用 `ChainParser.parse_to_multi_chain` 保留所有候选，交给下游策略来做最终选择。

```python
ambiguous_text = """
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

non_strict = NUMERIC_DOT_PATTERN_BUILDER.modify(
    prefix_regex=r"[\#\s]*",
    suffix_regex=r"[\.\s]*",
    separator=r"[\.\s]+",
    is_sep_regex=True,
    min_level=2,
).build()

patterns = [
    ENGLISH_CHAPTER_PATTERN_BUILDER.build(),
    NUMERIC_DOT_PATTERN_BUILDER.build(),
    non_strict,
]

parser = ChainParser(patterns)
multi_chain = parser.parse_to_multi_chain(ambiguous_text)

print(TreeExporter.export_chain(multi_chain))

builder = TreeBuilder()
tree_from_multi = builder.build_tree(multi_chain)
print(TreeExporter.export_tree(tree_from_multi))
```

示例输出：

```
[LEVEL-[]: ROOT]
[LEVEL-[2]: Building Blocks]
[LEVEL-[2, 1]: A Component, LEVEL-[2, 1]: A Component]
[LEVEL-[2, 1, 1]: A details, LEVEL-[2, 1, 1]: A details]
[LEVEL-[2, 1]: 2 A details 2 [...], LEVEL-[2, 1, 2]: A details 2 [...]]
[LEVEL-[2, 2]: 2-Sided Materials B Component, LEVEL-[2, 2, 2]: -Sided Materials B Component]

ROOT
└─ Chapter 2 Building Blocks
    ├─ 2.1 A Component
    │   ├─ 2.1.1 A details
    │   └─ 2.1 .2 A details 2 [...]
    └─ 2.2 2-Sided Materials B Component
```

要点：

* 外层列表仍按照文本行顺序排列（第一项保持 `ROOT`）。
* 内层列表按检测顺序/priority 排列。TreeBuilder 会优先选择能与上一节点 `is_imm_next` 的候选，否则回退到 `pattern_priority` 最低的节点。
* `TreeExporter.export_chain` 在多候选模式下用方括号展示整行候选，可快速定位 OCR 误差或歧义标题。

## 功能详解

### 内置和自定义模式

可以使用 `NUMERIC_DOT_PATTERN_BUILDER`、`CHINESE_CHAPTER_PATTERN_BUILDER` 等构建器快速解析常见格式，也可以通过 `PatternBuilder` 自定义前缀、后缀、数字类型和分隔符。

```python
# 示例：匹配 "第A节."，"第B节."
letter_section_pattern = PatternBuilder(
    prefix_regex=r"第",
    number_type=NumberType.LETTER,
    suffix_regex=r"节"
).build()
```

### 智能纠错（AutoPruneStrategy）

实际文档往往不够规范。`AutoPruneStrategy`（`TreeBuilder` 的默认策略）可以处理常见问题，比如标题编号跳跃（例如，`1.1` 后面直接是 `1.3`）以及误识别为标题的文本行，相比 `StrictStrategy` 能提供更稳定的解析结果。

**示例：处理不完美**

考虑以下文本，其中缺少一个章节（`1.2`），并且包含一行可能被误认为是标题的文本：

**输入文本：**

```text
第一章 基础
    第一章的介绍内容。

1.1 核心概念
    基本思想的解释。
    本节奠定了基础。

# 注意：这里缺少标题 '1.2 中级概念'。

1.3 高级主题
    讨论更复杂的主题。我们在
    1.1节的基础上进行讨论。本节更深入且更为详细。
    # 注意：这里的 '1.1.' 是正文文本（正文文本刚好在此处换行），不是标题。

第二章 构建模块
    第二章的内容。

2.1 组件 A
    关于第一个组件的详细信息。

2.2 组件 B
    关于第二个组件的详细信息。文档结束。
```

**中间链结构（修剪前）：**

一个简单的解析步骤可能会产生如下链结构，包括误识别的标题：

```
LEVEL-[]: ROOT
LEVEL-[1]: 基础
LEVEL-[1, 1]: 核心概念
LEVEL-[1, 3]: 高级主题
LEVEL-[1, 1]: 本节更深入且更为详细。  <-- 潜在误报
LEVEL-[2]: 构建模块
LEVEL-[2, 1]: 组件 A
LEVEL-[2, 2]: 组件 B
```

**AutoPrune 的工作原理：**

构建树时，`AutoPruneStrategy` 分析序列：

1. 它识别出 `LEVEL-[1, 3]` 可以合理地跟在 `LEVEL-[1, 1]` 之后，即使缺少 `[1, 2]`（兄弟跳跃）。
2. 它看到后面的 `LEVEL-[1, 1]` 节点（"本节更深入且更为详细。"）后接一个完全不同的层次结构（`LEVEL-[2]`）。这种不连续性强烈表明第二个 `LEVEL-[1, 1]` 节点是误报。
3. 该策略"修剪"误识别的节点，将其内容有效地合并回前一个有效节点（在此情况下为 `LEVEL-[1, 3]`，具体取决于内容关联的实现细节）。

**最终树结构（修剪后）：**

生成的树正确反映了预期的文档结构：

```
ROOT
├─ 第一章 基础
│   ├─ 1.1 核心概念
│   └─ 1.3 高级主题  # 正确处理了跳跃并忽略误报
└─ 第二章 构建模块
    ├─ 2.1 组件 A
    └─ 2.2 组件 B
```

### 节点操作与可逆性

ArborParser 使用 `ChainNode`（线性序列）和 `TreeNode`（树形结构）对象。它们都继承自 `BaseNode`，包含 `level_seq`、`title` 和原始 `content` 字符串。

* **内容合并：** 可以将一个节点的内容合并到另一个节点。这在处理非标题文本或修正错误时特别有用。
    ```python
    # 将节点 B 的内容添加到节点 A
    node_a.concat_node(node_b)
    ```

* **子节点合并：** 父节点可以合并其所有子节点的内容。
    ```python
    # 让 node_a 包含自身内容以及所有子节点的内容
    node_a.merge_all_children()
    ```

* **重建原始文本：** 由于每个节点都保存了原始文本块（`content`），您可以从根 `TreeNode` 重建完整文档。这可以验证解析的准确性，也支持修改后重新生成。
    ```python
    # 从解析后的树形结构获取完整文本
    reconstructed_text = root_node.get_full_content()
    assert reconstructed_text == original_text # 验证
    ```

## 应用场景

* 文档解析
* 法律文档分析（法律文件、合同）
* 大纲处理与转换
* 报告结构化与分析
* 内容管理系统导入
* 结构化文本数据提取
* 格式转换（如文本转 HTML/XML 并保持结构）
* RAG 的智能分块策略

## 贡献

欢迎贡献（Pull Request、 Issue）！

## 许可证

MIT 许可证。
