"""Основная логика работы с таблицами базы данных."""

from primitive_db.constants import (
    COLUMN_SEPARATOR,
    ID_COLUMN,
    ID_TYPE,
    VALID_TYPES,
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
        if not separator or not name or column_type not in VALID_TYPES:
            raise ValueError(f"Некорректное значение: {column}. Попробуйте снова.")
        if name == ID_COLUMN and column_type == ID_TYPE:
            continue
        if name in schema:
            raise ValueError(f"Некорректное значение: {column}. Попробуйте снова.")
        schema[name] = column_type
    return schema


def create_table(metadata: dict, table_name: str, columns: list[str]) -> dict | None:
    """Создает новую таблицу в метаданных.

    Столбец ID:int добавляется автоматически в начало списка столбцов.

    Args:
        metadata: текущие метаданные базы данных.
        table_name: имя новой таблицы.
        columns: список столбцов вида "имя:тип".

    Returns:
        Обновленные метаданные или None, если таблицу создать не удалось.

    Side effects:
        Изменяет словарь metadata и выводит сообщение в консоль.
    """
    if table_name in metadata:
        print(f'Ошибка: Таблица "{table_name}" уже существует.')
        return None
    try:
        schema = parse_columns(columns)
    except ValueError as error:
        print(error)
        return None

    metadata[table_name] = schema
    columns_text = ", ".join(
        f"{name}{COLUMN_SEPARATOR}{column_type}"
        for name, column_type in schema.items()
    )
    print(f'Таблица "{table_name}" успешно создана со столбцами: {columns_text}')
    return metadata


def drop_table(metadata: dict, table_name: str) -> dict | None:
    """Удаляет таблицу из метаданных.

    Args:
        metadata: текущие метаданные базы данных.
        table_name: имя удаляемой таблицы.

    Returns:
        Обновленные метаданные или None, если таблицы не существует.

    Side effects:
        Изменяет словарь metadata и выводит сообщение в консоль.
    """
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return None
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
