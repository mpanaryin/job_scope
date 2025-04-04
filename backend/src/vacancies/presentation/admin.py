from sqladmin import ModelView

from src.vacancies.infrastructure.db.orm import Vacancy


class VacancyAdmin(ModelView, model=Vacancy):
    column_list = [Vacancy.id, Vacancy.name, Vacancy.salary_from, Vacancy.salary_to]
    form_excluded_columns = ["meta"]
