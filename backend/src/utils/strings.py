import logging
import random
import string
from typing import Optional

logger = logging.getLogger(__name__)

ALPHA_NUM = string.ascii_letters + string.digits


def generate_random_alphanum(length: int = 20) -> str:
    """Создание случайной последовательности символов, состоящей только из букв и цифр"""
    return "".join(random.choices(ALPHA_NUM, k=length))


def string_list_to_int_list(string_list: list | str | None) -> Optional[list[int]]:
    """
    Преобразование списка строк в список целых чисел.
    Специальная функция под запросы, где ID выводятся как список строк.
    """
    if not string_list or string_list == ['']:
        return []
    if isinstance(string_list, str):
        return [int(number) for number in string_list.split(',')]
    elif isinstance(string_list, list):
        return [int(number) for number in string_list[0].split(',')]
