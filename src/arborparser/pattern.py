from dataclasses import dataclass, field, replace
from typing import List, Callable
import re
from arborparser.utils import (
    roman_to_int,
    chinese_to_int,
    ALL_CHINESE_CHARS,
    ALL_ROMAN_NUMERALS,
)


@dataclass(frozen=True)
class NumberTypeInfo:
    pattern: str
    converter: Callable[[str], int]  # 将字符串转换为整数
    name: str


class NumberType:
    ARABIC = NumberTypeInfo(pattern=r"\d+", converter=int, name="arabic")
    ROMAN = NumberTypeInfo(
        pattern=f"[{ALL_ROMAN_NUMERALS}]+", converter=roman_to_int, name="roman"
    )
    CHINESE = NumberTypeInfo(
        pattern=f"[{ALL_CHINESE_CHARS}]+",
        converter=chinese_to_int,
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
    regex: re.Pattern[str]
    converter: Callable[
        [re.Match[str]], List[int]
    ]  # 将regex匹配结果转换为层级列表（例如[1,2,3]）
    description: str


@dataclass(frozen=True)
class PatternBuilder:
    prefix_regex: str = ""
    number_type: NumberTypeInfo = field(default_factory=lambda: NumberType.ARABIC)
    suffix_regex: str = r"\s+"
    separator: str = "."
    min_level: int = 1
    max_level: int = 32

    def __post_init__(self) -> None:

        # 检查分隔符是否是单个字符
        if len(self.separator) > 1:
            raise ValueError(f"Separator {self.separator} must be a single character")

        # 检查prefix和suffix是否是有效的正则表达式
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

    def modify(self, **kwargs) -> "PatternBuilder":  # type: ignore
        return replace(self, **kwargs)

    def build(self) -> LevelPattern:
        number_pattern = self.number_type.pattern
        # 构建正则表达式，加入层级限制
        level_range_pattern = (
            f"(?:{re.escape(self.separator)}{number_pattern})"
            f"{{{self.min_level - 1},{self.max_level - 1}}}"
        )
        pattern = f"^{self.prefix_regex}({number_pattern}{level_range_pattern}){self.suffix_regex}"

        def converter(match: re.Match[str]) -> List[int]:
            numbers = match.group(1).split(self.separator)
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


# 预定义的模式构建器
CHINESE_CHAPTER_PATTERN_BUILDER = PatternBuilder(
    prefix_regex=r"第?",
    number_type=NumberType.CHINESE,
    suffix_regex=r"[章回篇节条款]+[\.、\s]*",
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
