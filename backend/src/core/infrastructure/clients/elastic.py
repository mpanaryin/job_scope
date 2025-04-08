from functools import lru_cache

from elasticsearch import AsyncElasticsearch

from src.core.config import settings


@lru_cache
def get_elastic_client() -> AsyncElasticsearch:
    """
    Create and cache an Elasticsearch client instance.

    This function initializes a singleton Elasticsearch client using the configured hosts.
    The use of `lru_cache` ensures that only one instance is created and reused throughout
    the application lifetime.

    :return: A cached AsyncElasticsearch client instance.
    """
    return AsyncElasticsearch(settings.ELASTICSEARCH_HOSTS)
