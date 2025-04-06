import logging

from fastapi import APIRouter, Depends

from src.crud.router import CRUDRouter
from src.vacancies.domain.dtos import VacancyCreateDTO, VacancyUpdateDTO, VacancyReadDTO
from src.vacancies.domain.entities import VacancySearchQuery
from src.vacancies.infrastructure.db.crud import VacancyService
from src.vacancies.presentation.bootstrap import get_vacancy_search_repo

logger = logging.getLogger(__name__)

vacancy_api_router = APIRouter()


class VacancyCRUDRouter(CRUDRouter):
    crud = VacancyService()
    create_schema = VacancyCreateDTO
    update_schema = VacancyUpdateDTO
    read_schema = VacancyReadDTO
    router = APIRouter()


@vacancy_api_router.get("/search")
async def search(query: VacancySearchQuery = Depends()):
    logger.info("Search logss")
    es_vacancy_repository = get_vacancy_search_repo()
    response = await es_vacancy_repository.search(query)
    return response["hits"]["hits"]
