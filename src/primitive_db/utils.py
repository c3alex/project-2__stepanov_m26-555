"""Вспомогательные функции для работы с файлами базы данных."""

import json

from primitive_db.constants import FILE_ENCODING, JSON_INDENT


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
