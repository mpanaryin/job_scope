from elasticsearch import AsyncElasticsearch

from src.core.config import settings
from src.vacancies.infrastructure.elastic.mappings import VACANCY_MAPPING


async def create_vacancy_index():
    """
    Create the Elasticsearch index for storing vacancies.

    Uses the predefined VACANCY_MAPPING and creates the index 'vacancies'.
    If the index already exists, the operation will be ignored.

    :return: Result of the Elasticsearch index creation.
    """
    async with AsyncElasticsearch(settings.ELASTICSEARCH_HOSTS) as es:
        result = await es.indices.create(index="vacancies", body=VACANCY_MAPPING, ignore=400)
        return result


async def delete_vacancy_index():
    """
    Delete the Elasticsearch index 'vacancies'.

    Useful for resetting the search database or during cleanup in test environments.

    :return: Result of the Elasticsearch index deletion.
    """
    async with AsyncElasticsearch(settings.ELASTICSEARCH_HOSTS) as es:
        result = await es.indices.delete(index="vacancies")
        return result
