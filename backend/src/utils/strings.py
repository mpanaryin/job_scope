import random
import string
from typing import Optional

ALPHA_NUM = string.ascii_letters + string.digits


def generate_random_alphanum(length: int = 20) -> str:
    """
    Generate a random alphanumeric string.

    This function returns a string of the specified length, consisting
    only of uppercase/lowercase letters and digits.

    :param length: Desired length of the generated string.
    :return: Random alphanumeric string.
    """
    return "".join(random.choices(ALPHA_NUM, k=length))


def string_list_to_int_list(string_list: list | str | None) -> Optional[list[int]]:
    """
    Convert a string or list of strings into a list of integers.

    This function is useful when parsing query parameters like `?ids=1,2,3`,
    which may come in as a string or a list of strings.

    :param string_list: Input data in the form of a string, a list of strings,
                        or None.
    :return: A list of integers parsed from the input, or an empty list.
    """
    if not string_list or string_list == ['']:
        return []
    if isinstance(string_list, str):
        return [int(number) for number in string_list.split(',')]
    elif isinstance(string_list, list):
        return [int(number) for number in string_list[0].split(',')]
