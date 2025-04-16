from pydantic import Field

from src.core.domain.entities import CustomModel


class HHClusterGroup(CustomModel):
    id: str | None = None
    name: str | None = None


class HHArgument(CustomModel):
    argument: str | None = None
    cluster_group: HHClusterGroup | None = None
    disable_url: str | None = None
    value: str | None = None
    value_description: str | None = None
    hex_color: str | None = None
    metro_type: str | None = None


class HHMetroStation(CustomModel):
    lat: float | None = None
    line_id: str | None = None
    line_name: str | None = None
    lng: float | None = None
    station_id: str | None = None
    station_name: str | None = None


class HHAddress(CustomModel):
    building: str | None = None
    city: str | None = None
    description: str | None = None
    lat: float | None = None
    lng: float | None = None
    metro_stations: list[HHMetroStation] | None = None
    street: str | None = None


class HHArea(CustomModel):
    id: str | None = None
    name: str | None = None
    url: str | None = None


class HHLogoUrl(CustomModel):
    original: str | None = None
    size_90: str | None = None
    size_240: str | None = None


class HHEmployer(CustomModel):
    accredited_it_employer: bool | None = None
    alternate_url: str | None = None
    id: str | None = None
    logo_urls: dict[str, str] | None = None
    name: str | None = None
    trusted: bool | None = None
    url: str | None = None


class HHEmployment(CustomModel):
    id: str | None = None
    name: str | None = None


class HHExperience(CustomModel):
    id: str | None = None
    name: str | None = None


class HHSalary(CustomModel):
    currency: str | None = None
    from_: int | None = Field(None, alias="from")
    gross: bool | None = None
    to: int | None = None


class HHSchedule(CustomModel):
    id: str | None = None
    name: str | None = None


class HHSnippet(CustomModel):
    requirement: str | None = None
    responsibility: str | None = None


class HHType(CustomModel):
    id: str | None = None
    name: str | None = None


class HHProfessionalRole(CustomModel):
    id: str | None = None
    name: str | None = None


class HHVacancy(CustomModel):
    accept_incomplete_resumes: bool | None = None
    address: HHAddress | None = None
    alternate_url: str | None = None
    apply_alternate_url: str | None = None
    archived: bool = False
    area: HHArea | None = None
    employer: HHEmployer | None = None
    employment: HHEmployment | None = None
    experience: HHExperience | None = None
    has_test: bool | None = None
    id: str
    name: str | None = None
    published_at: str | None = None
    created_at: str | None = None
    response_letter_required: bool | None = None
    salary: HHSalary | None = None
    schedule: HHSchedule | None = None
    snippet: HHSnippet | None = None
    type: HHType | None = None
    url: str | None = None
    professional_roles: list[HHProfessionalRole] | None = None


class HHVacancyResponse(CustomModel):
    arguments: list[HHArgument] | None = None
    clusters: dict | None = None
    fixes: dict | None = None
    found: int | None = None
    items: list[HHVacancy] | None = None
    page: int | None = None
    pages: int | None = None
    per_page: int | None = None
    suggests: dict | None = None
