import asyncio
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.vacancies.elastic.indices import delete_vacancy_index


async def main():
    """Usage: python delete_elastic_indices.py"""
    result = await delete_vacancy_index()
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
