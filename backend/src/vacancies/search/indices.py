from elasticsearch import AsyncElasticsearch

from src.core.config import settings
from src.vacancies.search.mappings import VACANCY_MAPPING


async def create_vacancy_index():
    """Создаёт индекс 'vacancies'"""
    # ignore=400 -> не создаст, если индекс уже есть
    async with AsyncElasticsearch(settings.ELASTICSEARCH_HOSTS) as es:
        result = await es.indices.create(index="vacancies", body=VACANCY_MAPPING, ignore=400)
        return result


async def delete_vacancy_index():
    """Удаляет индекс 'vacancies'"""
    async with AsyncElasticsearch(settings.ELASTICSEARCH_HOSTS) as es:
        result = await es.indices.delete(index="vacancies")
        return result
