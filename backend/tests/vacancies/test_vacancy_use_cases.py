import pytest
from unittest.mock import AsyncMock, MagicMock

from src.vacancies.application.mappers.vacancies import VacancyAPIToDomainMapper
from src.vacancies.application.use_cases.vacancy_collector import collect_all_vacancies
from src.vacancies.domain.entities import Vacancy, VacancySource
from src.core.domain.entities import BulkResult
from tests.vacancies.fakes import FakeVacancyUnitOfWork, FakeSearchVacancyRepository


@pytest.mark.asyncio
async def test_collect_all_vacancies(monkeypatch):
    # Arrange
    search_params = {"query": "python"}
    fake_vacancy = MagicMock()
    domain_vacancy = Vacancy(source_id="1", source_name=VacancySource.HEADHUNTER)

    # mocks
    mock_client = AsyncMock()
    mock_client.get_all_vacancies.return_value = [fake_vacancy]

    # подменим маппер
    monkeypatch.setattr(
        VacancyAPIToDomainMapper,
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

    mock_client.get_all_vacancies.assert_awaited_once_with(search_params)
    assert result == {
        "database": db_result,
        "search_db": search_result
    }
