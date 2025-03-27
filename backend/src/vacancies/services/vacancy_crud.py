from src.crud.base import CRUDBase
from src.vacancies import orm


class VacancyService(CRUDBase, model=orm.Vacancy):
    ...
