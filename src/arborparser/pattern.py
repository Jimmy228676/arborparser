from dataclasses import dataclass, field, replace
from typing import List, Callable, Any
import re
from arborparser.utils import (
    roman_to_int,
    chinese_to_int,
    ALL_CHINESE_CHARS,
    ALL_ROMAN_NUMERALS,
)


@dataclass(frozen=True)
class NumberTypeInfo:
    """
    Information about a number type, including its regex pattern and conversion method.

    Attributes:
        pattern (str): The regex pattern to match this number type.
        converter (Callable[[str], int]): Function to convert matched strings to integers.
        name (str): The name of the number type.
    """

    pattern: str
    converter: Callable[[str], int]
    name: str


def _safe_roman_converter(roman_str: str) -> int:
    """Safe Roman numeral converter that always returns an int."""
    result = roman_to_int(roman_str)
    if result is None:
        raise ValueError(f"Invalid Roman numeral: {roman_str}")
    return result


def _safe_chinese_converter(chinese_str: str) -> int:
    """Safe Chinese numeral converter that always returns an int."""
    result = chinese_to_int(chinese_str)
    if result is None:
        raise ValueError(f"Invalid Chinese numeral: {chinese_str}")
    return result


class NumberType:
    """
    Class containing different types of number information.
    """

    ARABIC = NumberTypeInfo(pattern=r"\d+", converter=int, name="arabic")
    ROMAN = NumberTypeInfo(
        pattern=f"[{ALL_ROMAN_NUMERALS}]+",
        converter=_safe_roman_converter,
        name="roman",
    )
    CHINESE = NumberTypeInfo(
        pattern=f"[{ALL_CHINESE_CHARS}]+",
        converter=_safe_chinese_converter,
        name="chinese",
    )
    LETTER = NumberTypeInfo(
        pattern=r"[A-Z]", converter=lambda x: ord(x) - ord("A") + 1, name="letter"
    )
    CIRCLED = NumberTypeInfo(
        pattern=r"[①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰⑱⑲⑳]",
        converter=lambda x: ord(x) - ord("①") + 1,
        name="circled",
    )


@dataclass
class LevelPattern:
    """
    A pattern for matching and converting text into a hierarchical list of integers.

    Attributes:
        regex (re.Pattern[str]): Compiled regex pattern for matching.
        converter (Callable[[re.Match[str]], List[int]]): Function to convert matches to a list of integers.
        description (str): Description of the pattern.
    """

    regex: re.Pattern[str]
    converter: Callable[[re.Match[str]], List[int]]
    description: str


@dataclass(frozen=True)
class PatternBuilder:
    """
    A builder for creating LevelPattern instances with configurable parameters.

    Attributes:
        prefix_regex (str): Regex pattern to match before the number sequence.
        number_type (NumberTypeInfo): Type of numbers to match and convert.
        suffix_regex (str): Regex pattern to match after the number sequence.
        separator (str): Character or regex used to separate numbers in the sequence.
        is_sep_regex (bool): Whether the separator should be interpreted as a regex.
        min_level (int): Minimum number of levels to match.
        max_level (int): Maximum number of levels to match.
    """

    prefix_regex: str = ""
    number_type: NumberTypeInfo = field(default_factory=lambda: NumberType.ARABIC)
    suffix_regex: str = r"\s+"
    separator: str = "."
    is_sep_regex: bool = False
    min_level: int = 1
    max_level: int = 32

    def __post_init__(self) -> None:
        """
        Validates the configuration of the PatternBuilder.
        """
        if self.is_sep_regex:
            try:
                re.compile(self.separator)
            except re.error:
                raise ValueError(f"Invalid regex pattern in separator: {self.separator}")
        elif len(self.separator) > 1:
            raise ValueError(f"Separator {self.separator} must be a single character")

        try:
            re.compile(self.prefix_regex)
        except re.error:
            raise ValueError(f"Invalid regex pattern in prefix: {self.prefix_regex}")

        try:
            re.compile(self.suffix_regex)
        except re.error:
            raise ValueError(f"Invalid regex pattern in suffix: {self.suffix_regex}")

        if self.min_level < 1:
            raise ValueError(f"Minimum level {self.min_level} must be greater than 0")
        if self.max_level < self.min_level:
            raise ValueError(
                f"Maximum level {self.max_level} must be greater than or equal to minimum level {self.min_level}"
            )

    def modify(self, **kwargs: Any) -> "PatternBuilder":
        """
        Create a new PatternBuilder with modified attributes.

        Args:
            **kwargs: Attributes to modify.

        Returns:
            PatternBuilder: A new instance with updated attributes.
        """
        return replace(self, **kwargs)

    def build(self) -> LevelPattern:
        """
        Build a LevelPattern from the current configuration.

        Returns:
            LevelPattern: Compiled pattern with conversion logic.
        """
        number_pattern = self.number_type.pattern
        separator_pattern = (
            self.separator if self.is_sep_regex else re.escape(self.separator)
        )
        level_range_pattern = (
            f"(?:{separator_pattern}{number_pattern})"
            f"{{{self.min_level - 1},{self.max_level - 1}}}"
        )
        pattern = rf"^\s*{self.prefix_regex}({number_pattern}{level_range_pattern}){self.suffix_regex}"

        split_regex = (
            re.compile(f"(?:{self.separator})") if self.is_sep_regex else None
        )

        def converter(match: re.Match[str]) -> List[int]:
            seq_text = match.group(1)
            if split_regex:
                numbers = [n for n in split_regex.split(seq_text) if n]
            else:
                numbers = seq_text.split(self.separator)
            if not (self.min_level <= len(numbers) <= self.max_level):
                raise ValueError(
                    f"Matched levels ({len(numbers)}) out of range "
                    f"[{self.min_level}, {self.max_level}]"
                )
            return [self.number_type.converter(n) for n in numbers]

        return LevelPattern(
            regex=re.compile(pattern),
            converter=converter,
            description=f"Match {self.number_type.__class__.__name__.lower()} numbers",
        )


# Predefined pattern builders
CHINESE_CHAPTER_PATTERN_BUILDER = PatternBuilder(
    prefix_regex=r"第?",
    number_type=NumberType.CHINESE,
    suffix_regex=r"[章回篇节条款]+[\.、\s]*",
)

ENGLISH_CHAPTER_PATTERN_BUILDER = PatternBuilder(
    prefix_regex=r"Chapter\s",
    number_type=NumberType.ARABIC,
    suffix_regex=r"[\.\s]*",
)

NUMERIC_DOT_PATTERN_BUILDER = PatternBuilder(
    number_type=NumberType.ARABIC, separator=r".", suffix_regex=r"[\.\s]*"
)

NUMERIC_DASH_PATTERN_BUILDER = PatternBuilder(
    number_type=NumberType.ARABIC, separator=r"-", suffix_regex=r"[\.\s]*"
)

ROMAN_PATTERN_BUILDER = PatternBuilder(
    number_type=NumberType.ROMAN, suffix_regex=r"[\.\s]*"
)

CIRCLED_PATTERN_BUILDER = PatternBuilder(
    number_type=NumberType.CIRCLED, suffix_regex=r"[\.\s]*"
)
