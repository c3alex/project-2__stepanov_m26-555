"""Запуск базы данных, основной цикл и разбор команд."""

import shlex

from prettytable import PrettyTable

from primitive_db import constants, core
from primitive_db.constants import (
    KEYWORD_FROM,
    KEYWORD_INTO,
    KEYWORD_SET,
    KEYWORD_VALUES,
    KEYWORD_WHERE,
    META_FILE,
    PROMPT_TEXT,
    RECORDS_NOT_FOUND_MESSAGE,
)
from primitive_db.decorators import handle_db_errors
from primitive_db.parser import (
    find_keyword,
    incorrect_value,
    parse_condition,
    parse_values,
)
from primitive_db.utils import (
    delete_table_data,
    load_metadata,
    load_table_data,
    save_metadata,
    save_table_data,
)


def print_help() -> None:
    """Выводит справку по доступным командам.

    Side effects:
        Печатает справку в консоль.
    """
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")

    print("\n***Операции с данными***")
    print("Функции:")
    print(
        "<command> insert into <имя_таблицы> values (<значение1>, <значение2>, ...)"
        " - создать запись."
    )
    print(
        "<command> select from <имя_таблицы> where <столбец> = <значение>"
        " - прочитать записи по условию."
    )
    print("<command> select from <имя_таблицы> - прочитать все записи.")
    print(
        "<command> update <имя_таблицы> set <столбец1> = <новое_значение1>"
        " where <столбец_условия> = <значение_условия> - обновить запись."
    )
    print(
        "<command> delete from <имя_таблицы> where <столбец> = <значение>"
        " - удалить запись."
    )
    print("<command> info <имя_таблицы> - вывести информацию о таблице.")

    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")


def split_where(text: str, user_input: str) -> tuple[str, dict]:
    """Отделяет обязательное where-условие от начала строки.

    Args:
        text: часть команды, содержащая "... where <условие>".
        user_input: исходная команда (для сообщения об ошибке).

    Returns:
        Кортеж (часть до where, разобранное where-условие).

    Raises:
        ValueError: если where-условие отсутствует или некорректно.
    """
    index = find_keyword(text, KEYWORD_WHERE)
    if index == -1:
        raise incorrect_value(user_input)
    head = text[:index].strip()
    where_clause = parse_condition(text[index + len(KEYWORD_WHERE) :])
    return head, where_clause


def print_records(records: list[dict], schema: dict[str, str]) -> None:
    """Выводит записи в виде таблицы PrettyTable.

    Args:
        records: список записей.
        schema: схема таблицы.

    Side effects:
        Печатает таблицу в консоль.
    """
    table = PrettyTable()
    table.field_names = list(schema)
    for record in records:
        table.add_row([record.get(column) for column in schema])
    print(table)


@handle_db_errors
def handle_create_table(metadata: dict, args: list[str], user_input: str) -> None:
    """Обрабатывает команду create_table.

    Args:
        metadata: метаданные базы данных.
        args: аргументы команды.
        user_input: исходная команда.

    Side effects:
        Сохраняет метаданные при успехе.
    """
    if len(args) < 2:
        raise incorrect_value(user_input)
    if core.create_table(metadata, args[1], args[2:]) is None:
        return
    save_metadata(META_FILE, metadata)


@handle_db_errors
def handle_drop_table(metadata: dict, args: list[str], user_input: str) -> None:
    """Обрабатывает команду drop_table.

    Args:
        metadata: метаданные базы данных.
        args: аргументы команды.
        user_input: исходная команда.

    Side effects:
        Сохраняет метаданные и удаляет файл данных таблицы при успехе.
    """
    if len(args) != 2:
        raise incorrect_value(user_input)
    core.get_schema(metadata, args[1])
    if core.drop_table(metadata, args[1]) is None:
        return
    save_metadata(META_FILE, metadata)
    delete_table_data(args[1])


@handle_db_errors
def handle_insert(metadata: dict, user_input: str) -> None:
    """Обрабатывает команду insert into <таблица> values (...).

    Args:
        metadata: метаданные базы данных.
        user_input: исходная команда.

    Side effects:
        Сохраняет данные таблицы при успехе.
    """
    parts = user_input.split(maxsplit=3)
    if (
        len(parts) != 4
        or parts[1].lower() != KEYWORD_INTO
        or not parts[3].lower().startswith(KEYWORD_VALUES)
    ):
        raise incorrect_value(user_input)
    table_name = parts[2]
    values = parse_values(parts[3][len(KEYWORD_VALUES) :])
    table_data = load_table_data(table_name)
    if core.insert(metadata, table_name, values, table_data) is None:
        return
    save_table_data(table_name, table_data)


@handle_db_errors
def handle_select(metadata: dict, user_input: str) -> None:
    """Обрабатывает команду select from <таблица> [where <условие>].

    Args:
        metadata: метаданные базы данных.
        user_input: исходная команда.

    Side effects:
        Выводит найденные записи в консоль.
    """
    parts = user_input.split(maxsplit=3)
    if len(parts) < 3 or parts[1].lower() != KEYWORD_FROM:
        raise incorrect_value(user_input)
    table_name = parts[2]
    where_clause = None
    if len(parts) == 4:
        head, where_clause = split_where(" " + parts[3], user_input)
        if head:
            raise incorrect_value(user_input)
    schema = core.get_schema(metadata, table_name)
    if where_clause:
        core.validate_clause(schema, where_clause)
    records = core.select(load_table_data(table_name), where_clause)
    if records is None:
        return
    print_records(records, schema)


@handle_db_errors
def handle_update(metadata: dict, user_input: str) -> None:
    """Обрабатывает команду update <таблица> set ... where ....

    Args:
        metadata: метаданные базы данных.
        user_input: исходная команда.

    Side effects:
        Сохраняет данные таблицы при успехе.
    """
    parts = user_input.split(maxsplit=3)
    if len(parts) != 4 or parts[2].lower() != KEYWORD_SET:
        raise incorrect_value(user_input)
    table_name = parts[1]
    set_text, where_clause = split_where(parts[3], user_input)
    set_clause = parse_condition(set_text)
    schema = core.get_schema(metadata, table_name)
    core.validate_clause(schema, set_clause)
    core.validate_clause(schema, where_clause)
    table_data = load_table_data(table_name)
    if core.update(table_data, set_clause, where_clause, table_name) is None:
        return
    save_table_data(table_name, table_data)


@handle_db_errors
def handle_delete(metadata: dict, user_input: str) -> None:
    """Обрабатывает команду delete from <таблица> where <условие>.

    Args:
        metadata: метаданные базы данных.
        user_input: исходная команда.

    Side effects:
        Сохраняет данные таблицы при успехе.
    """
    parts = user_input.split(maxsplit=3)
    if len(parts) != 4 or parts[1].lower() != KEYWORD_FROM:
        raise incorrect_value(user_input)
    table_name = parts[2]
    head, where_clause = split_where(" " + parts[3], user_input)
    if head:
        raise incorrect_value(user_input)
    schema = core.get_schema(metadata, table_name)
    core.validate_clause(schema, where_clause)
    table_data = load_table_data(table_name)
    if not core.filter_records(table_data, where_clause):
        raise ValueError(RECORDS_NOT_FOUND_MESSAGE)
    if core.delete(table_data, where_clause, table_name) is None:
        return
    save_table_data(table_name, table_data)


@handle_db_errors
def handle_info(metadata: dict, args: list[str], user_input: str) -> None:
    """Обрабатывает команду info <таблица>.

    Args:
        metadata: метаданные базы данных.
        args: аргументы команды.
        user_input: исходная команда.

    Side effects:
        Выводит информацию о таблице.
    """
    if len(args) != 2:
        raise incorrect_value(user_input)
    core.info(metadata, args[1], load_table_data(args[1]))


def execute_command(metadata: dict, user_input: str) -> bool:
    """Выполняет одну команду пользователя.

    Args:
        metadata: метаданные базы данных.
        user_input: введенная строка.

    Returns:
        False, если нужно завершить работу, иначе True.
    """
    try:
        args = shlex.split(user_input)
    except ValueError:
        args = user_input.split()
    command = args[0].lower()

    match command:
        case constants.COMMAND_EXIT:
            return False
        case constants.COMMAND_HELP:
            print_help()
        case constants.COMMAND_LIST_TABLES:
            core.list_tables(metadata)
        case constants.COMMAND_CREATE_TABLE:
            handle_create_table(metadata, args, user_input)
        case constants.COMMAND_DROP_TABLE:
            handle_drop_table(metadata, args, user_input)
        case constants.COMMAND_INSERT:
            handle_insert(metadata, user_input)
        case constants.COMMAND_SELECT:
            handle_select(metadata, user_input)
        case constants.COMMAND_UPDATE:
            handle_update(metadata, user_input)
        case constants.COMMAND_DELETE:
            handle_delete(metadata, user_input)
        case constants.COMMAND_INFO:
            handle_info(metadata, args, user_input)
        case _:
            print(f"Функции {args[0]} нет. Попробуйте снова.")
    return True


def run() -> None:
    """Запускает основной цикл базы данных.

    Side effects:
        Читает команды из стандартного ввода, выводит результаты в консоль,
        сохраняет метаданные и данные таблиц в файлы.
    """
    print("***База данных***")
    print_help()

    while True:
        metadata = load_metadata(META_FILE)
        try:
            user_input = input(PROMPT_TEXT).strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if user_input and not execute_command(metadata, user_input):
            break
