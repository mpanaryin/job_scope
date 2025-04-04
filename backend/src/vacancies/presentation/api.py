import logging

from fastapi import APIRouter, Depends

from src.crud.router import CRUDRouter
from src.vacancies.domain import schemas
from src.vacancies.domain.schemas import VacancySearchQuery
from src.vacancies.infrastructure.db.crud import VacancyService
from src.vacancies.presentation.bootstrap import get_vacancy_search_repo

logger = logging.getLogger(__name__)

router = APIRouter()


class VacancyCRUDRouter(CRUDRouter):
    crud = VacancyService()
    create_schema = schemas.VacancyCreate
    update_schema = schemas.VacancyUpdate
    read_schema = schemas.VacancyRead
    router = APIRouter()


@router.get("/search")
async def search(query: VacancySearchQuery = Depends()):
    logger.info("Search logss")
    es_vacancy_repository = get_vacancy_search_repo()
    response = await es_vacancy_repository.search(query)
    return response["hits"]["hits"]
