from pydantic import Field

from src.core.schemas import CustomModel


class ClusterGroup(CustomModel):
    id: str | None = None
    name: str | None = None


class Argument(CustomModel):
    argument: str | None = None
    cluster_group: ClusterGroup | None = None
    disable_url: str | None = None
    value: str | None = None
    value_description: str | None = None
    hex_color: str | None = None
    metro_type: str | None = None


class MetroStation(CustomModel):
    lat: float | None = None
    line_id: str | None = None
    line_name: str | None = None
    lng: float | None = None
    station_id: str | None = None
    station_name: str | None = None


class Address(CustomModel):
    building: str | None = None
    city: str | None = None
    description: str | None = None
    lat: float | None = None
    lng: float | None = None
    metro_stations: list[MetroStation] | None = None
    street: str | None = None


class Area(CustomModel):
    id: str | None = None
    name: str | None = None
    url: str | None = None


class LogoUrl(CustomModel):
    original: str | None = None
    size_90: str | None = None
    size_240: str | None = None


class Employer(CustomModel):
    accredited_it_employer: bool | None = None
    alternate_url: str | None = None
    id: str | None = None
    logo_urls: dict[str, str] | None = None
    name: str | None = None
    trusted: bool | None = None
    url: str | None = None


class Employment(CustomModel):
    id: str | None = None
    name: str | None = None


class Experience(CustomModel):
    id: str | None = None
    name: str | None = None


class Salary(CustomModel):
    currency: str | None = None
    from_: int | None = Field(None, alias="from")
    gross: bool | None = None
    to: int | None = None


class Schedule(CustomModel):
    id: str | None = None
    name: str | None = None


class Snippet(CustomModel):
    requirement: str | None = None
    responsibility: str | None = None


class Type(CustomModel):
    id: str | None = None
    name: str | None = None


class ProfessionalRole(CustomModel):
    id: str | None = None
    name: str | None = None


class VacancyItem(CustomModel):
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
    id: str | None = None
    name: str | None = None
    published_at: str | None = None
    created_at: str | None = None
    response_letter_required: bool | None = None
    salary: Salary | None = None
    schedule: Schedule | None = None
    snippet: Snippet | None = None
    type: Type | None = None
    url: str | None = None
    professional_roles: list[ProfessionalRole] | None = None


class VacancyResponse(CustomModel):
    arguments: list[Argument] | None = None
    clusters: dict | None = None
    fixes: dict | None = None
    found: int | None = None
    items: list[VacancyItem] | None = None
    page: int | None = None
    pages: int | None = None
    per_page: int | None = None
    suggests: dict | None = None
