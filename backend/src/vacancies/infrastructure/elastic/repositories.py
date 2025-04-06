from elasticsearch import helpers

from src.core.schemas import BulkResult
from src.db.elastic import es_client
from src.vacancies.application.mappers.vacancies import VacancyDomainToElasticMapper
from src.vacancies.domain.entities import Vacancy, VacancySearchQuery
from src.vacancies.domain.interfaces import IVacancySearchRepository


class ESVacancySearchRepository(IVacancySearchRepository):
    """ElasticSearch Vacancy Search Repository"""

    async def bulk_add(self, vacancies: list[Vacancy]) -> BulkResult:
        vacancies = VacancyDomainToElasticMapper().map(vacancies)
        success, failed = await helpers.async_bulk(es_client, vacancies)
        return BulkResult(success=success, failed=failed, total=len(vacancies))

    async def search(self, query: VacancySearchQuery):
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

        response = await es_client.search(index="vacancies", body=body)
        return response
