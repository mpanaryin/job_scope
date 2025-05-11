from src.crud.base import CRUDBase
from src.vacancies.infrastructure.db import orm


class VacancyService(CRUDBase, model=orm.VacancyDB):
    """
    Service layer for managing Vacancy CRUD operations.

    Inherits from CRUDBase and operates on the `orm.Vacancy` model.
    Can be extended to implement business-specific logic around vacancies.
    """

