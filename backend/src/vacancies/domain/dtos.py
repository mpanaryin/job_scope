import datetime
import uuid

from pydantic import AnyUrl, field_serializer

from src.core.domain.entities import CustomModel
from src.vacancies.domain.entities import VacancySource


class VacancyReadDTO(CustomModel):
    """DTO for reading vacancy data."""
    id: uuid.UUID
    # Source
    source_name: VacancySource
    source_id: int
    url: AnyUrl
    # Name
    name: str
    description: str | None = None
    # Salary
    salary_from: int | None = None
    salary_to: int | None = None
    salary_currency: str | None = None
    salary_gross: bool | None = None
    # Employer
    area_name: str | None = None
    employer_name: str | None = None
    # Requirement
    employment: str | None = None
    experience: str | None = None
    schedule: str | None = None
    has_test: bool
    # Additional
    is_archived: bool = False
    type: str | None = None
    meta: dict
    # Dates
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
    """DTO for creating a vacancy."""
    # Source
    source_name: VacancySource
    source_id: int
    url: AnyUrl
    # Name
    name: str
    description: str | None = None
    # Salary
    salary_from: int | None = None
    salary_to: int | None = None
    salary_currency: str | None = None
    salary_gross: bool | None = None
    # Employer
    area_name: str | None = None
    employer_name: str | None = None
    # Requirement
    employment: str | None = None
    experience: str | None = None
    schedule: str | None = None
    has_test: bool
    # Additional
    is_archived: bool = False
    type: str | None = None
    meta: dict
    # Dates
    created_at: datetime.datetime | None = None
    published_at: datetime.datetime | None = None

    @field_serializer("url")
    def convert_url(self, v):
        return str(v)

    @field_serializer("source_name")
    def convert_source_name(self, v):
        return v.value


class VacancyUpdateDTO(CustomModel):
    """DTO for updating a vacancy"""
    source_name: VacancySource | None = None
    source_id: int | None = None
    url: AnyUrl | None = None
    # Name
    name: str | None = None
    description: str | None = None
    # Salary
    salary_from: int | None = None
    salary_to: int | None = None
    salary_currency: str | None = None
    salary_gross: bool | None = None
    # Employer
    area_name: str | None = None
    employer_name: str | None = None
    # Requirement
    employment: str | None = None
    experience: str | None = None
    schedule: str | None = None
    has_test: bool | None = None
    # Additional
    is_archived: bool = False
    type: str | None = None
    meta: dict | None = None
    # Dates
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
