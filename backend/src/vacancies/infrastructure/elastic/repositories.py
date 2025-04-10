from elasticsearch import helpers

from src.core.domain.entities import BulkResult
from src.core.infrastructure.clients.elastic import get_elastic_client
from src.vacancies.application.mappers.vacancies import VacancyDomainToElasticMapper
from src.vacancies.domain.entities import Vacancy, VacancySearchQuery
from src.vacancies.domain.interfaces import IVacancySearchRepository


class ESVacancySearchRepository(IVacancySearchRepository):
    """
    ElasticSearch implementation of the IVacancySearchRepository interface.

    Provides full-text search and bulk insert capabilities for vacancies using Elasticsearch.

    Attributes:
        es_client: Async Elasticsearch client instance.
    """

    def __init__(self):
        """
        Initialize the search repository with an Elasticsearch client.
        """
        self.es_client = get_elastic_client()

    async def bulk_add(self, vacancies: list[Vacancy]) -> BulkResult:
        """
        Insert or update multiple vacancies in Elasticsearch.

        :param vacancies: List of domain-level Vacancy models.
        :return: BulkResult with counts of successful and failed operations.
        """
        vacancies = VacancyDomainToElasticMapper().map(vacancies)
        success, failed = await helpers.async_bulk(self.es_client, vacancies)
        return BulkResult(success=success, failed=failed, total=len(vacancies))

    async def search(self, query: VacancySearchQuery):
        """
        Execute a search query in the 'vacancies' index.

        Builds a bool query using provided filters such as area, employer, experience, employment type, schedule,
        test requirement, archive status, and published date range.

        :param query: Structured search query.
        :return: Raw Elasticsearch response containing matched documents.
        """
        must_clauses = []

        if query.query:
            must_clauses.append({"match": {"name": query.query}})
        if query.area:
            must_clauses.append({"match": {"area.name": query.area}})
        if query.employer:
            must_clauses.append({"match": {"employer.name": query.employer}})
        if query.experience:
            must_clauses.append({"match": {"experience.name": query.experience}})
        if query.employment:
            must_clauses.append({"match": {"employment.name": query.employment}})
        if query.schedule:
            must_clauses.append({"match": {"schedule.name": query.schedule}})
        if query.has_test is not None:
            must_clauses.append({"term": {"has_test": query.has_test}})
        if query.is_archived is not None:
            must_clauses.append({"term": {"is_archived": query.is_archived}})
        if query.published_from or query.published_to:
            range_filter = {}
            if query.published_from:
                range_filter["gte"] = query.published_from.isoformat()
            if query.published_to:
                range_filter["lte"] = query.published_to.isoformat()
            must_clauses.append({"range": {"published_at": range_filter}})

        body = {
            "query": {
                "bool": {
                    "must": must_clauses
                }
            },
            "from": query.page * query.size,
            "size": query.size
        }

        if query.sort_by:
            body["sort"] = [{query.sort_by: {"order": query.sort_order}}]
        response = await self.es_client.search(index="vacancies", body=body)
        return response
