from typing import Optional

ALL_ROMAN_NUMERALS = "IVXLCDMivxlcdm"
ALL_CHINESE_CHARS = "0０零○〇洞1１一壹ㄧ弌么2２二貳贰弍兩两3３三參叁弎参叄4４四肆䦉刀5５五伍6６六陸陆7７七柒拐8８八捌杯9９九玖勾十拾什呀百佰千仟萬万億亿兆京經经垓秭杼穰壤溝沟澗涧正載極"


def roman_to_int(roman_str: str) -> Optional[int]:
    """
    Convert a Roman numeral string to an integer.
    Args:
        s: A string containing valid Roman numerals (I, V, X, L, C, D, M)
    Returns:
        The integer value of the Roman numeral, or None if the input is invalid
    """
    roman_numerals = {
        "I": 1,
        "V": 5,
        "X": 10,
        "L": 50,
        "C": 100,
        "D": 500,
        "M": 1000,
        "IV": 4,
        "IX": 9,
        "XL": 40,
        "XC": 90,
        "CD": 400,
        "CM": 900,
    }

    # Input validation
    if not isinstance(roman_str, str):
        return None

    # Normalize the input string (remove spaces and convert to uppercase)
    normalized_str = "".join(roman_str.upper().split())

    # Validate that all characters are valid Roman numerals
    if not all(c in ALL_ROMAN_NUMERALS for c in normalized_str):
        return None

    result = 0
    index = 0
    str_length = len(normalized_str)

    while index < str_length:
        # Check for two-character Roman numerals first
        if index + 1 < str_length:
            two_chars = normalized_str[index : index + 2]
            if two_chars in roman_numerals:
                result += roman_numerals[two_chars]
                index += 2
                continue

        # Handle single character Roman numerals
        current_char = normalized_str[index]
        if current_char in roman_numerals:
            result += roman_numerals[current_char]
            index += 1
        else:
            return None

    return result


def chinese_to_int(chinese_str: str) -> Optional[int]:
    """将中文数字转换为阿拉伯数字。

    Args:
        chinese_str: 中文数字字符串，支持简体、繁体和其他变体

    Returns:
        转换后的整数，如果输入无效则返回None
    """
    digit_chars = [
        "0０零○〇洞",
        "1１一壹ㄧ弌么",
        "2２二貳贰弍兩两",
        "3３三參叁弎参叄",
        "4４四肆䦉刀",
        "5５五伍",
        "6６六陸陆",
        "7７七柒拐",
        "8８八捌杯",
        "9９九玖勾",
    ]
    unit_chars = ["十拾什呀", "百佰", "千仟"]
    magnitude_chars = [
        "萬万",  # 10^4
        "億亿",  # 10^8
        "兆",  # 10^12
        "京經经",  # 10^16
        "垓",  # 10^20
        "秭杼",  # 10^24
        "穰壤",  # 10^28
        "溝沟",  # 10^32
        "澗涧",  # 10^36
        "正",  # 10^40
        "載",  # 10^44
        "極",  # 10^48
    ]

    def get_digit_value(char: str) -> int:
        return next((i for i, chars in enumerate(digit_chars) if char in chars), -1)

    def get_unit_value(char: str) -> int:
        return next((i for i, chars in enumerate(unit_chars) if char in chars), -1)

    def get_magnitude_value(char: str) -> int:
        return next((i for i, chars in enumerate(magnitude_chars) if char in chars), -1)

    # 预处理：移除空白并处理符号
    normalized_str = "".join(chinese_str.split())
    sign = -1 if normalized_str.startswith(("負", "负")) else 1
    if normalized_str.startswith(("正", "負", "负")):
        normalized_str = normalized_str[1:]

    # 处理纯数字情况
    if all(any(c in chars for chars in digit_chars) for c in normalized_str):
        result = sum(
            get_digit_value(c) * (10**i) for i, c in enumerate(reversed(normalized_str))
        )
        return result * sign

    # 处理"十"开头的特殊情况（如"十一"表示"一十一"）
    if any(normalized_str.startswith(c) for c in unit_chars[0]):
        normalized_str = "一" + normalized_str

    # 处理带单位的数字
    current_sum = 0
    section_value = 0
    digit_value = 0

    for char in normalized_str:
        digit = get_digit_value(char)
        if digit != -1:
            digit_value = digit
            continue

        unit = get_unit_value(char)
        if unit != -1:
            section_value += digit_value * (10 ** (unit + 1))
            digit_value = 0
            continue

        magnitude = get_magnitude_value(char)
        if magnitude != -1:
            section_value += digit_value
            if magnitude <= 2:  # 处理万、亿、兆
                current_sum += section_value * (10 ** (4 * (magnitude + 1)))
            else:  # 处理更大的数值
                current_sum += section_value * pow(10, 4 * (magnitude + 1))
            section_value = digit_value = 0
            continue

        return None  # 遇到无效字符

    final_result = current_sum + section_value + digit_value
    return final_result * sign


if __name__ == "__main__":
    chinese_patterns_test = [
        # 基本数字
        "零",
        "一",
        "二",
        "九",
        # 特殊写法
        "壹",
        "贰",
        "陆",
        "柒",
        "捌",
        "玖",
        # 十位数
        "十",
        "十一",
        "二十",
        "九十九",
        # 百位数
        "一百",
        "一百零一",
        "一百一十",
        "一百二十八",
        "九百九十九",
        # 千位数
        "一千",
        "一千零一",
        "一千零十",
        "一千一百",
        "一千二百三十四",
        "九千八百七十六",
        # 万位数
        "一万",
        "一万零一",
        "一万零百",
        "一万零十",
        "一万一千",
        "一万零一百",
        "一万零一十",
        "一万一千零一",
        "一万二千三百四十五",
        # 十万位数
        "十万",
        "十万零一",
        "二十万零一",
        "九十九万九千九百九十九",
        # 亿位数
        "一亿",
        "一亿零一",
        "一亿零一万",
        "一亿零十万",
        "一亿二千三百四十五万六千七百八十九",
        "五亿零三百二十万零一百零一",
        # 更大的数
        "一兆",
        "一京",
        "一垓",
        "一秭",
        "一穰",
        # 带正负号
        "正一",
        "负一",
        "正十亿",
        "负十亿",
        # 繁体写法
        "壹佰贰拾叁",
        "貳仟參佰肆拾伍",
        "陸萬柒仟捌佰玖拾",
        # 混合写法
        "一億二千萬",
        "一亿零兩千萬",
        "壹億零二千万",
        # 零的特殊用法
        "一万零零零一",
        "一亿零零零零一",
        "十亿零五",
        # 特殊格式
        "廿一",  # 应返回None，不支持古体字
        "卅二",  # 应返回None，不支持古体字
        "正负一",  # 应返回None，符号冲突
        "一百萬億",  # 应返回None，单位顺序错误
        # 包含空格
        "一 二 三",
        "一万 零 一",
        "  一亿  二千万  ",
        # 边界测试
        "零零零零",
        "一零零零",
        "九九九九",
        "九千九百九十九万九千九百九十九",
        " ",
    ]

    for pattern in chinese_patterns_test:
        print(f"{pattern}=>{chinese_to_int(pattern)}")

    roman_patterns_test = [
        # 基本数字 (1-10)
        "I",
        "II",
        "III",
        "IV",
        "V",
        "VI",
        "VII",
        "VIII",
        "IX",
        "X",
        # 十位数 (11-99)
        "XI",
        "XIV",
        "XV",
        "XIX",
        "XX",
        "XL",
        "XLIV",
        "XLV",
        "XLIX",
        "L",
        "LI",
        "XC",
        "XCIX",
        # 百位数 (100-999)
        "C",
        "CI",
        "CX",
        "CD",
        "CDI",
        "CDXLIX",
        "D",
        "DI",
        "DCCC",
        "CM",
        "CMXCIX",
        # 千位数 (1000-3999)
        "M",
        "MI",
        "MX",
        "MC",
        "MCD",
        "MD",
        "MCM",
        "MCMXCIX",
        "MM",
        "MMM",
        "MMMCMXCIX",
        # 小写测试
        "i",
        "iv",
        "xl",
        "cd",
        "cm",
        "mcmxcix",
        # 混合大小写
        "IvXlCdM",
        "MCmXCiX",
        # 边界测试
        "",
        " ",
        "IIII",
        "MMMM",
        # 非法字符
        "ABC",
        "XIVY",
        "123",
        "M1CM",
        "I.V",
        "I-V",
        # 带空格
        "X I",
        " MC ",
        "M C M",
        # 复杂组合测试
        "MDCLXVI",  # 1666
        "MCMXCIX",  # 1999
        "MMCDXXI",  # 2421
        "MMDCCCXLV",  # 2845
        "MMMDCCCLXXXVIII",  # 3888
    ]

    for pattern in roman_patterns_test:
        result = roman_to_int(pattern)
        print(f"'{pattern}' => {result}")
