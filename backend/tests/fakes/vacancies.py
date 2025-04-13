from src.core.domain.entities import BulkResult
from src.vacancies.domain.entities import Vacancy, VacancySearchQuery
from src.vacancies.domain.interfaces import IVacancyRepository, IVacancyUnitOfWork, IVacancySearchRepository


class FakeVacancyRepository(IVacancyRepository):

    def __init__(self):
        self._vacancies = []

    async def bulk_add_or_update(self, vacancies: list[Vacancy]) -> BulkResult:
        created, updated = 0, 0
        for vacancy in vacancies:
            for i, v in enumerate(self._vacancies):
                if v.source_id == vacancy.source_id and v.source_name == vacancy.source_name:
                    self._vacancies[i] = vacancy
                    updated += 1
                    break
            else:
                self._vacancies.append(vacancy)
                created += 1
        total = len(vacancies)
        return BulkResult(
            success=created + updated,
            failed=total - (created + updated),
            total=total
        )


class FakeVacancyUnitOfWork(IVacancyUnitOfWork):
    users: IVacancyRepository

    def __init__(self):
        self.vacancies = FakeVacancyRepository()
        self.committed = False

    async def _commit(self):
        self.committed = True

    async def rollback(self):
        pass


class FakeSearchVacancyRepository(IVacancySearchRepository):

    def __init__(self):
        self._vacancies = []

    async def bulk_add(self, vacancies: list[Vacancy]) -> BulkResult:
        created, updated = 0, 0
        for vacancy in vacancies:
            for i, v in enumerate(self._vacancies):
                if v.source_id == vacancy.source_id and v.source_name == vacancy.source_name:
                    v[i] = vacancy
                    updated += 1
                    break
            else:
                self._vacancies.append(vacancy)
                created += 1
        total = len(vacancies)
        return BulkResult(
            success=created + updated,
            failed=total - (created + updated),
            total=total
        )

    async def search(self, query: VacancySearchQuery):
        for vacancy in self._vacancies:
            if query.query.lower() in vacancy.name.lower():
                return {"hits": {"hits": [vacancy]}}
        return {"hits": {"hits": []}}
