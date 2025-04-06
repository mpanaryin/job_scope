from elasticsearch import AsyncElasticsearch

from src.core.config import settings
from src.vacancies.infrastructure.elastic.mappings import VACANCY_MAPPING


async def create_vacancy_index():
    """Создаёт индекс 'vacancies'"""
    async with AsyncElasticsearch(settings.ELASTICSEARCH_HOSTS) as es:
        # ignore=400 -> не создаст, если индекс уже есть
        result = await es.indices.add(index="vacancies", body=VACANCY_MAPPING, ignore=400)
        return result


async def delete_vacancy_index():
    """Удаляет индекс 'vacancies'"""
    async with AsyncElasticsearch(settings.ELASTICSEARCH_HOSTS) as es:
        result = await es.indices.delete_by_pk(index="vacancies")
        return result
