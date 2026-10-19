"""Декораторы базы данных и замыкание для кэширования."""

import time
from typing import Callable

from primitive_db.constants import CONFIRM_ANSWER, TIME_PRECISION


def copy_metadata(wrapper: Callable, func: Callable) -> Callable:
    """Переносит имя и документацию исходной функции на обертку.

    Args:
        wrapper: функция-обертка.
        func: исходная функция.

    Returns:
        Обертка с именем и docstring исходной функции.
    """
    wrapper.__name__ = func.__name__
    wrapper.__qualname__ = func.__qualname__
    wrapper.__doc__ = func.__doc__
    wrapper.__wrapped__ = func
    return wrapper


def handle_db_errors(func: Callable) -> Callable:
    """Перехватывает ошибки базы данных и выводит их пользователю.

    Обрабатываются FileNotFoundError, KeyError (нет таблицы или столбца)
    и ValueError (ошибки валидации). При ошибке обертка возвращает None.

    Args:
        func: оборачиваемая функция.

    Returns:
        Функция-обертка.
    """

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError:
            print(
                "Ошибка: Файл данных не найден. "
                "Возможно, база данных не инициализирована."
            )
        except KeyError as error:
            print(f"Ошибка: {error.args[0]}")
        except ValueError as error:
            print(error)
        except Exception as error:
            print(f"Произошла непредвиденная ошибка: {error}")
        return None

    return copy_metadata(wrapper, func)


def confirm_action(action_name: str) -> Callable:
    """Создает декоратор, запрашивающий подтверждение опасной операции.

    Args:
        action_name: название действия для вопроса пользователю.

    Returns:
        Декоратор. Если пользователь ответил не "y", операция отменяется
        и обертка возвращает None.
    """

    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            question = f'Вы уверены, что хотите выполнить "{action_name}"? [y/n]: '
            try:
                answer = input(question)
            except EOFError:
                answer = ""
            if answer.strip().lower() != CONFIRM_ANSWER:
                print("Операция отменена.")
                return None
            return func(*args, **kwargs)

        return copy_metadata(wrapper, func)

    return decorator


def log_time(func: Callable) -> Callable:
    """Замеряет и выводит время выполнения функции.

    Args:
        func: оборачиваемая функция.

    Returns:
        Функция-обертка.

    Side effects:
        Печатает "Функция <имя> выполнилась за X.XXX секунд."
    """

    def wrapper(*args, **kwargs):
        start = time.monotonic()
        result = func(*args, **kwargs)
        elapsed = time.monotonic() - start
        print(
            f"Функция {func.__name__} выполнилась за "
            f"{elapsed:.{TIME_PRECISION}f} секунд."
        )
        return result

    return copy_metadata(wrapper, func)


def create_cacher() -> Callable:
    """Создает функцию кэширования, хранящую кэш в замыкании.

    Returns:
        Функция cache_result(key, value_func): возвращает значение из кэша
        по ключу, а при его отсутствии вызывает value_func, сохраняет
        результат в кэш и возвращает его.
    """
    cache = {}

    def cache_result(key, value_func: Callable):
        if key not in cache:
            cache[key] = value_func()
        return cache[key]

    return cache_result
