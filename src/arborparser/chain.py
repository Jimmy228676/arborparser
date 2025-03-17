from typing import List, Tuple, Optional

from arborparser.node import ChainNode
from arborparser.pattern import LevelPattern


class ChainParser:

    def __init__(
        self,
        patterns: List[LevelPattern],
    ):
        """
        :param patterns: 正则模式列表，格式为 (正则表达式, 转换函数)
                         转换函数将匹配结果转为层级列表
        """
        self.patterns = patterns
        self.current_content: List[str] = []  # 当前收集的内容缓冲区

    def parse_to_chain(self, text: str) -> List[ChainNode]:
        """核心链式解析逻辑"""
        chain: List[ChainNode] = []
        for line in text.split("\n"):
            line = line.strip()
            if not line:
                continue
            line = line + "\n"

            # 尝试匹配标题模式
            if (chain_node := self._detect_level(line)) is not None:
                # 遇到新标题时，提交前一个节点的内容
                if chain:
                    chain[-1].content = "\n".join(self.current_content)
                    self.current_content = []
                chain.append(chain_node)
            else:
                self.current_content.append(line)

        # 处理最后一个节点的内容
        if chain and self.current_content:
            chain[-1].content = "\n".join(self.current_content)
        return chain

    def _detect_level(self, line: str) -> Optional[ChainNode]:
        """应用所有模式检测标题层级"""
        for priority, pattern in enumerate(self.patterns):
            if match := pattern.regex.match(line):
                try:
                    level_seq = pattern.converter(match)
                    level_text = match.group(0)
                    title = line[len(level_text) :].strip()
                    return ChainNode(
                        level_seq=level_seq,
                        level_text=level_text.strip(),
                        title=title,
                        pattern_priority=priority,
                    )
                except ValueError:
                    continue
        return None
