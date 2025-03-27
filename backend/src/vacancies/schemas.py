import datetime
import uuid
from enum import Enum
from typing import Literal

from pydantic import AnyUrl, field_serializer, Field

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
    # Даты
    created_at: datetime.datetime | None = None
    published_at: datetime.datetime | None = None
    updated_at: datetime.datetime | None = None

    def unique_id(self):
        return f'{self.source_name}_{self.source_id}'

    @field_serializer("url")
    def convert_url(self, v):
        return str(v)

    @field_serializer("source_name")
    def convert_source_name(self, v):
        return v.value

    class Config:
        from_attributes = True


class VacancyCreate(CustomModel):
    """Данные по вакансии для создания"""
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
    # Даты
    created_at: datetime.datetime | None = None
    published_at: datetime.datetime | None = None

    @field_serializer("url")
    def convert_url(self, v):
        return str(v)

    @field_serializer("source_name")
    def convert_source_name(self, v):
        return v.value


class VacancyUpdate(CustomModel):
    """Данные по вакансии для обновления"""
    source_name: VacancySource | None = None
    source_id: int | None = None
    url: AnyUrl | None = None
    # Название вакансии
    name: str | None = None
    description: str | None = None
    # Зарплата
    salary_from: int | None = None
    salary_to: int | None = None
    salary_currency: str | None = None
    salary_gross: bool | None = None
    # Данные по работодателю
    area_name: str | None = None
    employer_name: str | None = None
    # Требования к вакансии
    employment: str | None = None
    experience: str | None = None
    schedule: str | None = None
    has_test: bool | None = None
    # Дополнительная информация
    is_archived: bool = False
    type: str | None = None
    meta: dict | None = None
    # Даты
    created_at: datetime.datetime | None = None
    published_at: datetime.datetime | None = None

    @field_serializer("url")
    def convert_url(self, v):
        if v:
            return str(v)

    @field_serializer("source_name")
    def convert_source_name(self, v):
        if v:
            return v.value


class VacancySearchQuery(CustomModel):
    query: str | None = Field(None, description="Поисковый запрос по названию вакансии")
    area: str | None = Field(None, description="Регион, например 'Москва'")
    employer: str | None = Field(None, description="Название работодателя")
    experience: str | None = Field(None, description="Опыт работы, например 'От 1 года до 3 лет'")
    employment: str | None = Field(None, description="Тип занятости")
    schedule: str | None = Field(None, description="График работы")
    published_from: datetime.date | None = None
    published_to: datetime.date | None = None
    has_test: bool | None = None
    is_archived: bool | None = None
    sort_by: Literal["published_at", "salary_from", "salary_to"] | None = None
    sort_order: Literal["asc", "desc"] = "desc"
    page: int = 0
    size: int = 10
