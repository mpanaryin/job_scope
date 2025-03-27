from fastapi import APIRouter, Depends

from src.crud.router import CRUDRouter
from src.vacancies import schemas
from src.vacancies.schemas import VacancySearchQuery
from src.vacancies.search.queries import search_vacancies
from src.vacancies.services.vacancy_crud import VacancyService

router = APIRouter()


class VacancyCRUDRouter(CRUDRouter):
    crud = VacancyService()
    create_schema = schemas.VacancyCreate
    update_schema = schemas.VacancyUpdate
    read_schema = schemas.Vacancy
    router = APIRouter()


@router.get("/search")
async def search(query: VacancySearchQuery = Depends()):
    response = await search_vacancies(query)
    return response["hits"]["hits"]
