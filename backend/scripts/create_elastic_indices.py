import asyncio
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.vacancies.infrastructure.elastic.indices import create_vacancy_index


async def main():
    """Usage: python create_elastic_indices.py"""
    result = await create_vacancy_index()
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
