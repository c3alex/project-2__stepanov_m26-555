"""Константы примитивной базы данных."""

META_FILE = "db_meta.json"
DATA_DIR = "data"
DATA_FILE_EXTENSION = ".json"
JSON_INDENT = 4
FILE_ENCODING = "utf-8"

ID_COLUMN = "ID"
ID_TYPE = "int"
VALID_TYPES = ("int", "str", "bool")
COLUMN_SEPARATOR = ":"

PROMPT_TEXT = ">>>Введите команду: "

QUOTE_CHARS = ("'", '"')
TRUE_LITERALS = ("true",)
FALSE_LITERALS = ("false",)
VALUES_SEPARATOR = ","
ASSIGNMENT_OPERATOR = "="
VALUES_OPEN_BRACKET = "("
VALUES_CLOSE_BRACKET = ")"

KEYWORD_INTO = "into"
KEYWORD_FROM = "from"
KEYWORD_VALUES = "values"
KEYWORD_WHERE = "where"
KEYWORD_SET = "set"
