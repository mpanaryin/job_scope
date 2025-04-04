from src.crud.base import CRUDBase
from src.vacancies.infrastructure.db import orm


class VacancyService(CRUDBase, model=orm.Vacancy):
    ...

