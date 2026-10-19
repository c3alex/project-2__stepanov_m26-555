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

CONFIRM_ANSWER = "y"
TIME_PRECISION = 3

COMMAND_EXIT = "exit"
COMMAND_HELP = "help"
COMMAND_LIST_TABLES = "list_tables"
COMMAND_CREATE_TABLE = "create_table"
COMMAND_DROP_TABLE = "drop_table"
COMMAND_INSERT = "insert"
COMMAND_SELECT = "select"
COMMAND_UPDATE = "update"
COMMAND_DELETE = "delete"
COMMAND_INFO = "info"

INCORRECT_VALUE_MESSAGE = "Некорректное значение: {value}. Попробуйте снова."
RECORDS_NOT_FOUND_MESSAGE = "Ошибка: Записи, удовлетворяющие условию, не найдены."
