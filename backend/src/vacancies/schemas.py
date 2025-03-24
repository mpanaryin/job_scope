import datetime
import uuid
from enum import Enum

from pydantic import AnyUrl

from src.core.schemas import CustomModel


class VacancySource(str, Enum):
    HEADHUNTER = 'headhunter'
    RABOTA = 'rabota'
    SUPERJOB = 'superjob'

    @property
    def label(self):
        return {
            self.HEADHUNTER: "HeadHunter",
            self.RABOTA: "Rabota",
            self.SUPERJOB: "SuperJob"
        }[self]


class Vacancy(CustomModel):
    """Данные по вакансии"""
    id: uuid.UUID
    # Источник вакансии
    source_name: VacancySource
    source_id: int
    url: AnyUrl
    # Название вакансии
    name: str
    description: str | None = None
    # Зарплата
    salary_from: int | None = None
    salary_to: int | None = None
    salary_currency: str | None = None
    salary_gross: bool | None = None
    # Даты
    published_at: datetime.datetime
    created_at: datetime.datetime | None = None
    # Данные по работодателю
    area_name: str | None = None
    employer_name: str | None = None
    # Требования к вакансии
    employment: str | None = None
    experience: str | None = None
    schedule: str | None = None
    has_test: bool
    # Дополнительная информация
    is_archived: bool = False
    type: str | None = None
    meta: dict

    def unique_id(self):
        return f'{self.source_name}_{self.source_id}'

    class Config:
        from_attributes = True






