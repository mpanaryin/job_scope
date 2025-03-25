from fastapi import APIRouter

from src.crud.router import CRUDRouter
from src.vacancies import schemas
from src.vacancies.services.vacancy import VacancyService


class VacancyCRUDRouter(CRUDRouter):
    crud = VacancyService()
    create_schema = schemas.VacancyCreate
    update_schema = schemas.VacancyUpdate
    read_schema = schemas.Vacancy
    router = APIRouter()
