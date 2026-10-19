"""Основная логика работы с таблицами и данными базы данных.

Функции модуля сообщают об ошибках исключениями: ValueError — при
некорректных значениях, KeyError — при обращении к несуществующей
таблице или столбцу. Сообщение исключения предназначено для пользователя.
Публичные операции обернуты декоратором handle_db_errors: он выводит
сообщение об ошибке и возвращает None.
"""

import json

from primitive_db.constants import (
    COLUMN_SEPARATOR,
    ID_COLUMN,
    ID_TYPE,
    RECORDS_NOT_FOUND_MESSAGE,
    VALID_TYPES,
)
from primitive_db.decorators import (
    confirm_action,
    create_cacher,
    handle_db_errors,
    log_time,
)
from primitive_db.parser import incorrect_value

select_cache = create_cacher()


def get_schema(metadata: dict, table_name: str) -> dict[str, str]:
    """Возвращает схему таблицы.

    Args:
        metadata: метаданные базы данных.
        table_name: имя таблицы.

    Returns:
        Словарь {имя_столбца: тип}.

    Raises:
        KeyError: если таблица не существует.
    """
    if table_name not in metadata:
        raise KeyError(f'Таблица "{table_name}" не существует.')
    return metadata[table_name]


def format_columns(schema: dict[str, str]) -> str:
    """Форматирует схему таблицы в строку вида "ID:int, name:str".

    Args:
        schema: словарь {имя_столбца: тип}.

    Returns:
        Строка с перечислением столбцов.
    """
    return ", ".join(
        f"{name}{COLUMN_SEPARATOR}{column_type}" for name, column_type in schema.items()
    )


def parse_columns(columns: list[str]) -> dict[str, str]:
    """Разбирает описания столбцов вида "имя:тип".

    Args:
        columns: список строк вида "name:str".

    Returns:
        Упорядоченный словарь {имя_столбца: тип}, где первым идет ID:int.

    Raises:
        ValueError: если описание столбца или тип данных некорректны.
    """
    schema = {ID_COLUMN: ID_TYPE}
    for column in columns:
        name, separator, column_type = column.partition(COLUMN_SEPARATOR)
        if not separator or not name.isidentifier() or column_type not in VALID_TYPES:
            raise incorrect_value(column)
        if name == ID_COLUMN and column_type == ID_TYPE:
            continue
        if name in schema:
            raise incorrect_value(column)
        schema[name] = column_type
    return schema


def check_value_type(value: object, column_type: str) -> bool:
    """Проверяет, соответствует ли значение типу столбца.

    Args:
        value: проверяемое значение.
        column_type: тип столбца (int, str или bool).

    Returns:
        True, если тип значения совпадает с типом столбца.
    """
    return type(value).__name__ == column_type


def validate_clause(schema: dict[str, str], clause: dict) -> None:
    """Проверяет столбцы и типы значений в where/set условии.

    Args:
        schema: схема таблицы.
        clause: условие вида {столбец: значение}.

    Raises:
        KeyError: если столбец не существует.
        ValueError: если тип значения не совпадает с типом столбца.
    """
    for column, value in clause.items():
        if column not in schema:
            raise KeyError(f'Столбец "{column}" не существует.')
        if not check_value_type(value, schema[column]):
            raise incorrect_value(value)


def matches(record: dict, where_clause: dict | None) -> bool:
    """Проверяет, удовлетворяет ли запись условию.

    Args:
        record: запись таблицы.
        where_clause: условие {столбец: значение} или None.

    Returns:
        True, если запись подходит под условие (или условие не задано).
    """
    if not where_clause:
        return True
    return all(record.get(column) == value for column, value in where_clause.items())


def filter_records(table_data: list[dict], where_clause: dict | None) -> list[dict]:
    """Возвращает записи таблицы, подходящие под условие (без кэша).

    Args:
        table_data: записи таблицы.
        where_clause: условие {столбец: значение} или None.

    Returns:
        Список подходящих записей (ссылки на записи table_data).
    """
    return [record for record in table_data if matches(record, where_clause)]


@handle_db_errors
def create_table(metadata: dict, table_name: str, columns: list[str]) -> dict:
    """Создает новую таблицу в метаданных.

    Столбец ID:int добавляется автоматически в начало списка столбцов.

    Args:
        metadata: текущие метаданные базы данных.
        table_name: имя новой таблицы.
        columns: список столбцов вида "имя:тип".

    Returns:
        Обновленные метаданные.

    Raises:
        ValueError: если таблица уже существует или столбцы некорректны.

    Side effects:
        Изменяет словарь metadata и выводит сообщение в консоль.
    """
    if not table_name.isidentifier():
        raise incorrect_value(table_name)
    if table_name in metadata:
        raise ValueError(f'Ошибка: Таблица "{table_name}" уже существует.')
    schema = parse_columns(columns)
    metadata[table_name] = schema
    print(
        f'Таблица "{table_name}" успешно создана со столбцами: {format_columns(schema)}'
    )
    return metadata


@handle_db_errors
@confirm_action("удаление таблицы")
def drop_table(metadata: dict, table_name: str) -> dict:
    """Удаляет таблицу из метаданных.

    Args:
        metadata: текущие метаданные базы данных.
        table_name: имя удаляемой таблицы.

    Returns:
        Обновленные метаданные.

    Raises:
        KeyError: если таблица не существует.

    Side effects:
        Изменяет словарь metadata и выводит сообщение в консоль.
    """
    get_schema(metadata, table_name)
    del metadata[table_name]
    print(f'Таблица "{table_name}" успешно удалена.')
    return metadata


def list_tables(metadata: dict) -> None:
    """Выводит список всех таблиц.

    Args:
        metadata: текущие метаданные базы данных.

    Side effects:
        Выводит имена таблиц в консоль.
    """
    if not metadata:
        print("Таблиц пока нет.")
        return
    for table_name in metadata:
        print(f"- {table_name}")


@handle_db_errors
@log_time
def insert(
    metadata: dict, table_name: str, values: list, table_data: list[dict]
) -> list[dict]:
    """Добавляет новую запись в таблицу.

    ID генерируется автоматически как max(ID) + 1.

    Args:
        metadata: метаданные базы данных.
        table_name: имя таблицы.
        values: значения всех столбцов, кроме ID, в порядке схемы.
        table_data: текущие записи таблицы.

    Returns:
        Обновленный список записей таблицы.

    Raises:
        KeyError: если таблица не существует.
        ValueError: если количество или типы значений некорректны.

    Side effects:
        Изменяет table_data и выводит сообщение в консоль.
    """
    schema = get_schema(metadata, table_name)
    columns = [column for column in schema if column != ID_COLUMN]
    if len(values) != len(columns):
        raise ValueError(
            f"Ошибка: ожидается значений: {len(columns)}, передано: {len(values)}."
        )
    for column, value in zip(columns, values):
        if not check_value_type(value, schema[column]):
            raise incorrect_value(value)

    new_id = max((record[ID_COLUMN] for record in table_data), default=0) + 1
    record = {ID_COLUMN: new_id, **dict(zip(columns, values))}
    table_data.append(record)
    print(f'Запись с ID={new_id} успешно добавлена в таблицу "{table_name}".')
    return table_data


@handle_db_errors
@log_time
def select(table_data: list[dict], where_clause: dict | None = None) -> list[dict]:
    """Выбирает записи таблицы.

    Результаты одинаковых запросов к одинаковым данным кэшируются.

    Args:
        table_data: записи таблицы.
        where_clause: условие {столбец: значение}; если не задано,
            возвращаются все записи.

    Returns:
        Список копий подходящих записей.
    """
    cache_key = json.dumps([table_data, where_clause], sort_keys=True)
    return select_cache(
        cache_key,
        lambda: [dict(record) for record in filter_records(table_data, where_clause)],
    )


@handle_db_errors
def update(
    table_data: list[dict], set_clause: dict, where_clause: dict, table_name: str
) -> list[dict]:
    """Обновляет записи, подходящие под условие.

    Args:
        table_data: записи таблицы.
        set_clause: новые значения {столбец: значение}.
        where_clause: условие отбора {столбец: значение}.
        table_name: имя таблицы (для сообщений).

    Returns:
        Измененный список записей таблицы.

    Raises:
        ValueError: если пытаются изменить ID или записи не найдены.

    Side effects:
        Изменяет table_data и выводит сообщения в консоль.
    """
    if ID_COLUMN in set_clause:
        raise ValueError(f"Ошибка: Столбец {ID_COLUMN} нельзя изменять.")
    found = filter_records(table_data, where_clause)
    if not found:
        raise ValueError(RECORDS_NOT_FOUND_MESSAGE)
    for record in found:
        record.update(set_clause)
        print(
            f'Запись с ID={record[ID_COLUMN]} в таблице "{table_name}" '
            "успешно обновлена."
        )
    return table_data


@handle_db_errors
@confirm_action("удаление записи")
def delete(table_data: list[dict], where_clause: dict, table_name: str) -> list[dict]:
    """Удаляет записи, подходящие под условие.

    Args:
        table_data: записи таблицы.
        where_clause: условие отбора {столбец: значение}.
        table_name: имя таблицы (для сообщений).

    Returns:
        Измененный список записей таблицы.

    Raises:
        ValueError: если записи не найдены.

    Side effects:
        Изменяет table_data и выводит сообщения в консоль.
    """
    found = filter_records(table_data, where_clause)
    if not found:
        raise ValueError(RECORDS_NOT_FOUND_MESSAGE)
    for record in found:
        table_data.remove(record)
        print(
            f"Запись с ID={record[ID_COLUMN]} успешно удалена "
            f'из таблицы "{table_name}".'
        )
    return table_data


@handle_db_errors
def info(metadata: dict, table_name: str, table_data: list[dict]) -> None:
    """Выводит информацию о таблице.

    Args:
        metadata: метаданные базы данных.
        table_name: имя таблицы.
        table_data: записи таблицы.

    Raises:
        KeyError: если таблица не существует.

    Side effects:
        Выводит имя, столбцы и количество записей в консоль.
    """
    schema = get_schema(metadata, table_name)
    print(f"Таблица: {table_name}")
    print(f"Столбцы: {format_columns(schema)}")
    print(f"Количество записей: {len(table_data)}")
