import logging
from typing import Annotated

from fastapi import APIRouter, Query

from src.crud.router import CRUDRouter
from src.vacancies.domain.dtos import VacancyCreateDTO, VacancyUpdateDTO, VacancyReadDTO
from src.vacancies.domain.entities import VacancySearchQuery
from src.vacancies.infrastructure.db.crud import VacancyService
from src.vacancies.presentation.dependencies import VacancySearchRepoDep

logger = logging.getLogger(__name__)

vacancy_api_router = APIRouter()


@vacancy_api_router.get("/search")
async def search(query: Annotated[VacancySearchQuery, Query()], search_repo: VacancySearchRepoDep):
    """
    Search for vacancies using full-text filters and parameters.
    """
    response = await search_repo.search(query)
    return response["hits"]["hits"]


class VacancyCRUDRouter(CRUDRouter):
    crud = VacancyService()
    create_schema = VacancyCreateDTO
    update_schema = VacancyUpdateDTO
    read_schema = VacancyReadDTO
    router = APIRouter()
