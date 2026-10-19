"""Вспомогательные функции для работы с файлами базы данных."""

import json
import os

from primitive_db.constants import (
    DATA_DIR,
    DATA_FILE_EXTENSION,
    FILE_ENCODING,
    JSON_INDENT,
)


def load_metadata(filepath: str) -> dict:
    """Загружает метаданные базы данных из JSON-файла.

    Args:
        filepath: путь к JSON-файлу с метаданными.

    Returns:
        Словарь с метаданными. Если файл не найден, возвращает пустой словарь.
    """
    try:
        with open(filepath, encoding=FILE_ENCODING) as file:
            return json.load(file)
    except FileNotFoundError:
        return {}


def save_metadata(filepath: str, data: dict) -> None:
    """Сохраняет метаданные базы данных в JSON-файл.

    Args:
        filepath: путь к JSON-файлу с метаданными.
        data: словарь с метаданными.

    Side effects:
        Перезаписывает файл filepath.
    """
    with open(filepath, "w", encoding=FILE_ENCODING) as file:
        json.dump(data, file, ensure_ascii=False, indent=JSON_INDENT)


def get_table_path(table_name: str) -> str:
    """Возвращает путь к JSON-файлу с данными таблицы.

    Args:
        table_name: имя таблицы.

    Returns:
        Путь вида data/<имя_таблицы>.json.
    """
    return os.path.join(DATA_DIR, f"{table_name}{DATA_FILE_EXTENSION}")


def load_table_data(table_name: str) -> list[dict]:
    """Загружает записи таблицы из файла data/<имя_таблицы>.json.

    Args:
        table_name: имя таблицы.

    Returns:
        Список записей. Если файл не найден, возвращает пустой список.
    """
    try:
        with open(get_table_path(table_name), encoding=FILE_ENCODING) as file:
            return json.load(file)
    except FileNotFoundError:
        return []


def save_table_data(table_name: str, data: list[dict]) -> None:
    """Сохраняет записи таблицы в файл data/<имя_таблицы>.json.

    Args:
        table_name: имя таблицы.
        data: список записей таблицы.

    Side effects:
        Создает директорию data/ при необходимости и перезаписывает файл.
    """
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(get_table_path(table_name), "w", encoding=FILE_ENCODING) as file:
        json.dump(data, file, ensure_ascii=False, indent=JSON_INDENT)


def delete_table_data(table_name: str) -> None:
    """Удаляет файл с данными таблицы, если он существует.

    Args:
        table_name: имя таблицы.

    Side effects:
        Удаляет файл data/<имя_таблицы>.json.
    """
    path = get_table_path(table_name)
    if os.path.exists(path):
        os.remove(path)
