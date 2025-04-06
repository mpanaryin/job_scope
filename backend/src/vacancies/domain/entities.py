import datetime
from enum import Enum
from typing import Literal

from pydantic import Field

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


class MetroStation(CustomModel):
    line_id: str | None = None
    line_name: str | None = None
    lat: float | None = None
    lng: float | None = None
    station_name: str | None = None


class Address(CustomModel):
    city: str | None = None
    street: str | None = None
    building: str | None = None
    description: str | None = None
    lat: float | None = None
    lng: float | None = None
    metro_stations: list[MetroStation] | None = None



class Area(CustomModel):
    name: str | None = None
    url: str | None = None


class Employer(CustomModel):
    accredited_it_employer: bool | None = None
    alternate_url: str | None = None
    name: str | None = None
    trusted: bool | None = None
    url: str | None = None


class Employment(CustomModel):
    name: str | None = None


class Experience(CustomModel):
    name: str | None = None


class Salary(CustomModel):
    currency: str | None = None
    from_: int | None = Field(None, alias="from")
    gross: bool | None = None
    to: int | None = None


class Schedule(CustomModel):
    name: str | None = None


class Type(CustomModel):
    name: str | None = None


class ProfessionalRole(CustomModel):
    name: str | None = None


class Vacancy(CustomModel):
    # Источник вакансии
    source_id: str
    source_name: VacancySource
    accept_incomplete_resumes: bool | None = None
    address: Address | None = None
    alternate_url: str | None = None
    apply_alternate_url: str | None = None
    archived: bool = False
    area: Area | None = None
    employer: Employer | None = None
    employment: Employment | None = None
    experience: Experience | None = None
    has_test: bool | None = None
    name: str | None = None
    published_at: str | None = None
    created_at: str | None = None
    response_letter_required: bool | None = None
    requirement: str | None = None
    responsibility: str | None = None
    salary: Salary | None = None
    schedule: Schedule | None = None
    type: Type | None = None
    url: str | None = None
    professional_roles: list[ProfessionalRole] | None = None

    @property
    def description(self) -> str | None:
        """Вспомогательная функция для получения описания вакансии"""
        requirement = self.requirement or ''
        responsibility = self.responsibility or ''
        description = f"{requirement}\n\n{responsibility}".strip()
        return description


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
