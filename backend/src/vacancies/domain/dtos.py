import datetime
import uuid
from typing import Literal

from pydantic import AnyUrl, field_serializer, Field

from src.core.schemas import CustomModel
from src.vacancies.domain.entities import VacancySource


class VacancyReadDTO(CustomModel):
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


class VacancyCreateDTO(CustomModel):
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


class VacancyUpdateDTO(CustomModel):
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
