"""Функции для разбора сложных команд: values, where и set."""

from primitive_db.constants import (
    ASSIGNMENT_OPERATOR,
    FALSE_LITERALS,
    QUOTE_CHARS,
    TRUE_LITERALS,
    VALUES_CLOSE_BRACKET,
    VALUES_OPEN_BRACKET,
    VALUES_SEPARATOR,
)


def incorrect_value(value: str) -> ValueError:
    """Создает исключение о некорректном значении.

    Args:
        value: значение, которое не удалось разобрать.

    Returns:
        Исключение ValueError с сообщением для пользователя.
    """
    return ValueError(f"Некорректное значение: {value}. Попробуйте снова.")


def split_outside_quotes(text: str, separator: str) -> list[str]:
    """Разбивает строку по разделителю, не учитывая разделители внутри кавычек.

    Args:
        text: исходная строка.
        separator: одиночный символ-разделитель.

    Returns:
        Список частей строки без пробелов по краям.

    Raises:
        ValueError: если в строке есть незакрытая кавычка.
    """
    parts = []
    current = []
    quote = None
    for char in text:
        if quote:
            if char == quote:
                quote = None
        elif char in QUOTE_CHARS:
            quote = char
        elif char == separator:
            parts.append("".join(current).strip())
            current = []
            continue
        current.append(char)
    if quote:
        raise incorrect_value(text)
    parts.append("".join(current).strip())
    return parts


def find_keyword(text: str, keyword: str) -> int:
    """Ищет отдельное слово keyword вне кавычек.

    Args:
        text: строка, в которой ведется поиск.
        keyword: искомое ключевое слово.

    Returns:
        Индекс начала ключевого слова или -1, если оно не найдено.
    """
    quote = None
    keyword_length = len(keyword)
    for index, char in enumerate(text):
        if quote:
            if char == quote:
                quote = None
            continue
        if char in QUOTE_CHARS:
            quote = char
            continue
        word = text[index : index + keyword_length]
        before = text[index - 1] if index > 0 else " "
        after_index = index + keyword_length
        after = text[after_index] if after_index < len(text) else " "
        if word.lower() == keyword and before.isspace() and after.isspace():
            return index
    return -1


def parse_literal(token: str) -> int | str | bool:
    """Преобразует текстовое значение в значение Python.

    Строки должны быть заключены в кавычки, логические значения
    записываются как true/false, целые числа — без кавычек.

    Args:
        token: текстовое представление значения.

    Returns:
        Значение типа str, bool или int.

    Raises:
        ValueError: если значение не удалось распознать.
    """
    token = token.strip()
    if len(token) >= 2 and token[0] in QUOTE_CHARS and token[-1] == token[0]:
        return token[1:-1]
    if token.lower() in TRUE_LITERALS:
        return True
    if token.lower() in FALSE_LITERALS:
        return False
    try:
        return int(token)
    except ValueError:
        raise incorrect_value(token) from None


def parse_values(text: str) -> list[int | str | bool]:
    """Разбирает список значений вида ("Sergei", 28, true).

    Args:
        text: строка со значениями в круглых скобках.

    Returns:
        Список значений.

    Raises:
        ValueError: если строка имеет неверный формат.
    """
    text = text.strip()
    if not (
        text.startswith(VALUES_OPEN_BRACKET) and text.endswith(VALUES_CLOSE_BRACKET)
    ):
        raise incorrect_value(text)
    inner = text[len(VALUES_OPEN_BRACKET) : -len(VALUES_CLOSE_BRACKET)]
    if not inner.strip():
        return []
    tokens = split_outside_quotes(inner, VALUES_SEPARATOR)
    return [parse_literal(token) for token in tokens]


def parse_condition(text: str) -> dict[str, int | str | bool]:
    """Разбирает условие вида 'age = 28' или 'age = 29, name = "Ivan"'.

    Используется для разбора where и set условий.

    Args:
        text: строка с условием.

    Returns:
        Словарь {столбец: значение}, например {'age': 28}.

    Raises:
        ValueError: если условие имеет неверный формат.
    """
    condition = {}
    for assignment in split_outside_quotes(text, VALUES_SEPARATOR):
        parts = split_outside_quotes(assignment, ASSIGNMENT_OPERATOR)
        if len(parts) != 2 or not parts[0] or not parts[1]:
            raise incorrect_value(assignment)
        column, raw_value = parts
        condition[column] = parse_literal(raw_value)
    return condition
