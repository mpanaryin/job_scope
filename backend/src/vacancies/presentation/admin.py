from sqladmin import ModelView

from src.vacancies.infrastructure.db.orm import VacancyDB


class VacancyAdmin(ModelView, model=VacancyDB):
    column_list = [VacancyDB.id, VacancyDB.name, VacancyDB.salary_from, VacancyDB.salary_to]
    form_excluded_columns = ["meta"]
