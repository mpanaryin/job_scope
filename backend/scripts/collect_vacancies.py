import asyncio
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.vacancies.presentation.tasks import collect_vacancies_task


def main():
    """Usage: python create_elastic_indices.py"""
    result = collect_vacancies_task()
    print(result)


if __name__ == "__main__":
    main()
