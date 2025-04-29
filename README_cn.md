好的，我会将示例中的英文改为中文，包括文本内容和代码中的模式构建器。以下是更改后的 README：

---

# ArborParser

ArborParser 是一个强大的 Python 库，旨在解析结构化文本文档并将其转换为基于层次结构标题的树形表示。它能够智能地处理各种编号方案和文档不一致问题，非常适合处理大纲、报告、技术文档、法律文本等。

## 功能特性

* **链式解析：** 将文本转换为线性序列（`ChainNode` 列表），表示文档的层次结构。
* **灵活的模式定义：** 使用正则表达式和特定的数字转换器（阿拉伯数字、罗马数字、中文、字母、圈号）定义自定义解析模式。
* **内置模式：** 提供常见标题样式的现成模式（如 `1.2.3`、`第1章`、`第一章` 等）。
* **强大的树构建：** 将线性链转换为真正的层次结构 `TreeNode`。
* **自动错误修正：** 包含 `AutoPruneStrategy`，智能处理跳过的标题级别或错误识别为标题的行。
* **节点操作：** 允许合并节点之间的内容（`concat_node`），以灵活处理非标题文本或修正解析错误。
* **可逆转换：** 保留原始文本，支持从树中完整重建文档（`tree.get_full_content()`）。
* **导出功能：** 将解析结构以多种格式输出（如人类可读的树视图）。

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

# 1. 定义解析模式
patterns = [
    CHINESE_CHAPTER_PATTERN_BUILDER.build(),
    NUMERIC_DOT_PATTERN_BUILDER.build(),
]

# 2. 将文本解析为链式结构
parser = ChainParser(patterns)
chain = parser.parse_to_chain(test_text)

# 3. 构建树（使用 AutoPrune 以提高鲁棒性）
builder = TreeBuilder(strategy=AutoPruneStrategy())
tree = builder.build_tree(chain)

# 4. 输出结构化树
print(TreeExporter.export_tree(tree))
```

## 功能特性详细说明

### 内置和自定义模式

使用诸如 `NUMERIC_DOT_PATTERN_BUILDER`、`CHINESE_CHAPTER_PATTERN_BUILDER` 等构建器快速解析常见格式，或使用 `PatternBuilder` 自定义定义前缀、后缀、数字类型和分隔符。

```python
# 例：匹配 "第A节."，"第B节."
letter_section_pattern = PatternBuilder(
    prefix_regex=r"第",
    number_type=NumberType.LETTER,
    suffix_regex=r"节"
).build()
```

### 自动错误修正（AutoPruneStrategy）

文档往往不够完美。`AutoPruneStrategy`（`TreeBuilder` 默认使用）处理常见问题，如跳过的标题编号（例如，`1.1` 后接 `1.3`）并修剪误匹配为标题的行，确保与 `StrictStrategy` 相比更为鲁棒的解析过程。

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
2. 它看到后面的 `LEVEL-[1, 1]` 节点（“本节更深入且更为详细。”）后接一个完全不同的层次结构（`LEVEL-[2]`）。这种不连续性强烈表明第二个 `LEVEL-[1, 1]` 节点是误报。
3. 该策略“修剪”误识别的节点，将其内容有效地合并回前一个有效节点（在此情况下为 `LEVEL-[1, 3]`，具体取决于内容关联的实现细节）。

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

ArborParser 使用 `ChainNode`（线性序列）和 `TreeNode`（层次结构树）对象。两者均继承自 `BaseNode`，存储 `level_seq`、`title` 和原始 `content` 字符串。

* **合并内容：** 您可以将一个节点的内容合并到另一个节点。这在内部用于将非标题文本与其前面的标题关联，或在错误修正期间合并节点。
    ```python
    # 将节点 B 的内容附加到节点 A
    node_a.concat_node(node_b)
    ```

* **合并子节点：** 父节点可以吸收其所有子节点的内容。
    ```python
    # 使 node_a 包含其自身内容加上所有子孙节点的内容...
    node_a.merge_all_children()
    ```

* **重构原始文本：** 因为每个节点保留其原始文本块（`content`），所以您可以从根 `TreeNode` 重构整个原始文档。这验证了解析的完整性，并允许在修改后重新生成。
    ```python
    # 从解析的树结构中获取完整文本
    reconstructed_text = root_node.get_full_content()
    assert reconstructed_text == original_text # 验证
    ```

## 潜在使用场景

* 文档解析
* 法律文档分析（法律、合同）
* 大纲处理与转换
* 报告结构化与分析
* 内容管理系统导入
* 从结构化文本中提取数据
* 格式转换（例如，文本到 HTML/XML 保留结构）
* RAG 的更好分块策略

## 贡献

欢迎贡献（Pull Request、 Issue）！

## 许可证

MIT 许可证。
