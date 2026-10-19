"""Запуск базы данных, основной цикл и разбор команд."""

import shlex

from primitive_db.constants import META_FILE, PROMPT_TEXT
from primitive_db.core import create_table, drop_table, list_tables
from primitive_db.utils import load_metadata, save_metadata


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

    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")


def run() -> None:
    """Запускает основной цикл базы данных.

    Side effects:
        Читает команды из стандартного ввода, выводит результаты в консоль
        и сохраняет метаданные в файл META_FILE.
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
        if not user_input:
            continue

        try:
            args = shlex.split(user_input)
        except ValueError:
            print(f"Некорректное значение: {user_input}. Попробуйте снова.")
            continue
        command = args[0]

        match command:
            case "exit":
                break
            case "help":
                print_help()
            case "list_tables":
                list_tables(metadata)
            case "create_table":
                if len(args) < 2:
                    print(f"Некорректное значение: {user_input}. Попробуйте снова.")
                    continue
                if create_table(metadata, args[1], args[2:]) is not None:
                    save_metadata(META_FILE, metadata)
            case "drop_table":
                if len(args) != 2:
                    print(f"Некорректное значение: {user_input}. Попробуйте снова.")
                    continue
                if drop_table(metadata, args[1]) is not None:
                    save_metadata(META_FILE, metadata)
            case _:
                print(f"Функции {command} нет. Попробуйте снова.")
