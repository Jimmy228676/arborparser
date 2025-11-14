from typing import List, Union, Sequence, Any
from arborparser.node import ChainNode
from arborparser.pattern import LevelPattern


class ChainParser:
    """
    Parses text into a sequence of ChainNodes using predefined patterns.

    Attributes:
        patterns (List[LevelPattern]): A list of regex patterns, each with a conversion function
                                       to transform matches into hierarchy lists.
    """

    def __init__(self, patterns: List[LevelPattern]):
        """
        Initializes the ChainParser with the given patterns.

        Args:
            patterns (List[LevelPattern]): List of regex patterns and conversion functions.
        """
        self.patterns = patterns

    def parse_to_multi_chain(self, text: str) -> List[List[ChainNode]]:
        """
        Parse text and return every ChainNode candidate detected per line.

        A line might match multiple patterns or a single pattern might produce multiple
        hierarchy sequences. Each inner list preserves the order of the candidates
        detected for that line.
        """
        return self._parse_to_chain(text, is_multi_chain=True)

    def parse_to_chain(self, text: str) -> List[ChainNode]:
        """
        Core parsing logic to convert text into a chain of nodes.

        Args:
            text (str): Input text to be parsed.

        Returns:
            List[ChainNode]: List of parsed ChainNodes.
        """
        return self._parse_to_chain(text, is_multi_chain=False)

    def _parse_to_chain(
        self, text: str, is_multi_chain: bool = False
    ) -> Union[List[ChainNode], List[List[ChainNode]]]:
        root = ChainNode(level_seq=[], level_text="", title="ROOT", pattern_priority=0)
        current_nodes: List[ChainNode] = [root]
        current_content: List[str] = []

        if is_multi_chain:
            multi_result: List[List[ChainNode]] = [[root]]
        else:
            chain: List[ChainNode] = [root]

        for line in text.split("\n"):
            stripped = line.strip()
            if not stripped:
                current_content.append(line)
                continue

            detected_nodes = self._detect_level(line, is_multi_chain=is_multi_chain)
            if detected_nodes:
                self._assign_content(
                    current_nodes, current_content, add_trailing_newline=True
                )
                current_nodes = detected_nodes
                current_content = [line]

                if is_multi_chain:
                    multi_result.append(detected_nodes)
                else:
                    chain.append(detected_nodes[0])
            else:
                current_content.append(line)

        self._assign_content(current_nodes, current_content, add_trailing_newline=False)
        return multi_result if is_multi_chain else chain

    @staticmethod
    def _assign_content(
        nodes: Sequence[ChainNode],
        content_lines: List[str],
        *,
        add_trailing_newline: bool,
    ) -> None:
        if not nodes:
            return

        content = "\n".join(content_lines)
        if add_trailing_newline:
            content += "\n"

        for node in nodes:
            node.content = content

    def _detect_level(self, line: str, is_multi_chain: bool = False) -> List[ChainNode]:
        """
        Apply all patterns to detect the title hierarchy.

        Args:
            line (str): Text line to analyze.

        Returns:
            List[ChainNode]: Detected ChainNodes (may be empty if nothing matches).
        """
        detected: List[ChainNode] = []
        for priority, pattern in enumerate(self.patterns):
            match = pattern.regex.match(line)
            if not match:
                continue

            try:
                level_sequences = self._normalize_level_sequences(
                    pattern.converter(match)
                )
            except ValueError:
                continue

            if not level_sequences:
                continue

            level_text = match.group(0)
            title = line[len(level_text) :].strip()

            nodes = [
                ChainNode(
                    level_seq=seq,
                    level_text=level_text.strip(),
                    title=title,
                    pattern_priority=priority,
                )
                for seq in level_sequences
            ]

            if nodes:
                if not is_multi_chain:
                    return [nodes[0]]
                detected.extend(nodes)

        return detected

    @staticmethod
    def _normalize_level_sequences(result: Any) -> List[List[int]]:
        """
        Ensure converter output is treated uniformly as a list of level sequences.
        """
        if not result:
            return []

        first = result[0]
        if isinstance(first, (list, tuple)):
            return [list(seq) for seq in result if seq]
        return [list(result)]
