import logging

from fastapi import APIRouter, Depends

from src.crud.router import CRUDRouter
from src.vacancies import schemas
from src.vacancies.schemas import VacancySearchQuery
from src.vacancies.search.queries import search_vacancies
from src.vacancies.services.vacancy_crud import VacancyService

logger = logging.getLogger(__name__)

router = APIRouter()


class VacancyCRUDRouter(CRUDRouter):
    crud = VacancyService()
    create_schema = schemas.VacancyCreate
    update_schema = schemas.VacancyUpdate
    read_schema = schemas.Vacancy
    router = APIRouter()


@router.get("/search")
async def search(query: VacancySearchQuery = Depends()):
    # from src.main import logger
    logger.info("Search logss")
    response = await search_vacancies(query)
    return response["hits"]["hits"]
