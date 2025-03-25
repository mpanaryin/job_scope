from sqladmin import ModelView

from src.vacancies.orm import Vacancy


class VacancyAdmin(ModelView, model=Vacancy):
    column_list = [Vacancy.id, Vacancy.name, Vacancy.salary_from, Vacancy.salary_to]