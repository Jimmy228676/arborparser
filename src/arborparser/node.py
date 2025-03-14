from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class BaseNode:
    """所有节点类型的基类"""

    level_seq: List[int]  # 层级序列（如 [1,2,3]）
    level_text: str = ""  # 层级文本（如 "1.2.3"）
    title: str = ""  # 原始标题文本，不包含层级信息
    content: str = ""  # 关联内容文本


@dataclass
class ChainNode(BaseNode):
    """链式结构的节点，仅保存平面信息"""

    pattern_priority: int = 0  # 匹配到的模式优先级，用于排序


@dataclass
class TreeNode(BaseNode):
    """树形结构的节点，包含层级关系"""

    parent: Optional["TreeNode"] = None
    children: List["TreeNode"] = field(default_factory=list)
