from typing import List, Optional
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

    def parse_to_chain(self, text: str) -> List[ChainNode]:
        """
        Core parsing logic to convert text into a chain of nodes.

        Args:
            text (str): Input text to be parsed.

        Returns:
            List[ChainNode]: List of parsed ChainNodes.
        """

        chain: List[ChainNode] = [
            ChainNode(level_seq=[], level_text="", title="ROOT", pattern_priority=0)
        ]
        current_content: List[str] = []

        for line in text.split("\n"):

            # Try to match title pattern
            if (line.strip()) and (
                (chain_node := self._detect_level(line)) is not None
            ):
                # Submit previous node's content when encountering a new title
                if chain:
                    chain[-1].content = "\n".join(current_content) + "\n"
                current_content = [line]
                chain.append(chain_node)
            else:
                current_content.append(line)

        # Handle the content of the last node
        if current_content:
            chain[-1].content = "\n".join(current_content)
        return chain

    def _detect_level(self, line: str) -> Optional[ChainNode]:
        """
        Apply all patterns to detect the title hierarchy.

        Args:
            line (str): Text line to analyze.

        Returns:
            Optional[ChainNode]: The detected ChainNode or None if no pattern matches.
        """
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
