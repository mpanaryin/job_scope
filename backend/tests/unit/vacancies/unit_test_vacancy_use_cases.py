import pytest
from unittest.mock import AsyncMock, MagicMock

from src.integrations.infrastructure.external_api.mappers import VacancyExternalToDomainMapper
from src.vacancies.application.use_cases.vacancy_collector import collect_all_vacancies
from src.vacancies.domain.entities import Vacancy, VacancySource
from src.core.domain.entities import BulkResult
from tests.fakes.vacancies import FakeVacancyUnitOfWork, FakeSearchVacancyRepository


@pytest.mark.asyncio
async def test_collect_all_vacancies(monkeypatch):
    """
    Test collecting and storing all vacancies from an external source.

    Ensures that:
    - External client is called with correct search parameters,
    - Vacancies are mapped to domain models,
    - They are saved to both the primary database and the search index,
    - The result reflects successful insertions.
    """
    # Arrange
    search_params = {"query": "python"}
    fake_vacancy = MagicMock()
    domain_vacancy = Vacancy(source_id="1", source_name=VacancySource.HEADHUNTER)

    mock_client = AsyncMock()
    mock_client.get_all_vacancies.return_value = [fake_vacancy]

    monkeypatch.setattr(
        VacancyExternalToDomainMapper,
        "map",
        lambda self, vacancies: [domain_vacancy]
    )

    mock_uow = FakeVacancyUnitOfWork()
    mock_search_repo = FakeSearchVacancyRepository()

    db_result = BulkResult(success=1, failed=0, total=1)
    search_result = BulkResult(success=1, failed=0, total=1)
    # Act
    result = await collect_all_vacancies(
        search_params=search_params,
        client=mock_client,
        uow=mock_uow,
        search_repo=mock_search_repo
    )
    # Assert
    mock_client.get_all_vacancies.assert_awaited_once_with(search_params)
    assert result == {
        "database": db_result,
        "search_db": search_result
    }
