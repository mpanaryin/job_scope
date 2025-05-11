from src.integrations.infrastructure.external_api.headhunter.schemas.response import (
    HHVacancy, HHMetroStation, HHAddress, HHArea, HHEmployer,
    HHEmployment, HHExperience, HHSalary, HHSchedule,
    HHType, HHProfessionalRole
)
from src.vacancies.domain.entities import (
    Vacancy, Address, Area, Employer, Employment, Experience, Salary,
    Schedule, Type, ProfessionalRole, MetroStation, VacancySource
)


class HHVacancyToDomainMapper:
    """Mapper for converting an HH vacancy to the domain model"""

    def map(self, vacancy: HHVacancy, source: VacancySource) -> Vacancy:
        return Vacancy(
            source_id=vacancy.id,
            source_name=source,
            name=vacancy.name,
            url=vacancy.url,
            alternate_url=vacancy.alternate_url,
            apply_alternate_url=vacancy.apply_alternate_url,
            archived=vacancy.archived,
            created_at=vacancy.created_at,
            published_at=vacancy.published_at,
            has_test=vacancy.has_test,
            response_letter_required=vacancy.response_letter_required,
            requirement=vacancy.snippet.requirement if vacancy.snippet else None,
            responsibility=vacancy.snippet.responsibility if vacancy.snippet else None,
            accept_incomplete_resumes=vacancy.accept_incomplete_resumes,

            area=self._map_area(vacancy.area),
            employer=self._map_employer(vacancy.employer),
            address=self._map_address(vacancy.address),
            employment=self._map_employment(vacancy.employment),
            experience=self._map_experience(vacancy.experience),
            salary=self._map_salary(vacancy.salary),
            schedule=self._map_schedule(vacancy.schedule),
            type=self._map_type(vacancy.type),
            professional_roles=self._map_roles(vacancy.professional_roles),
        )

    def _map_area(self, area: HHArea | None) -> Area | None:
        if not area:
            return None
        return Area(name=area.name, url=area.url)

    def _map_employer(self, emp: HHEmployer | None) -> Employer | None:
        if not emp:
            return None
        return Employer(
            accredited_it_employer=emp.accredited_it_employer,
            alternate_url=emp.alternate_url,
            name=emp.name,
            trusted=emp.trusted,
            url=emp.url
        )

    def _map_employment(self, employment: HHEmployment | None) -> Employment | None:
        if not employment:
            return None
        return Employment(name=employment.name)

    def _map_experience(self, exp: HHExperience | None) -> Experience | None:
        if not exp:
            return None
        return Experience(name=exp.name)

    def _map_salary(self, salary: HHSalary | None) -> Salary | None:
        if not salary:
            return None
        return Salary(
            from_=salary.from_,
            to=salary.to,
            currency=salary.currency,
            gross=salary.gross
        )

    def _map_schedule(self, schedule: HHSchedule | None) -> Schedule | None:
        if not schedule:
            return None
        return Schedule(name=schedule.name)

    def _map_type(self, type_: HHType | None) -> Type | None:
        if not type_:
            return None
        return Type(name=type_.name)

    def _map_roles(self, roles: list[HHProfessionalRole] | None) -> list[ProfessionalRole] | None:
        if not roles:
            return None
        return [ProfessionalRole(name=role.name) for role in roles if role.name]

    def _map_address(self, address: HHAddress | None) -> Address | None:
        if not address:
            return None
        return Address(
            building=address.building,
            city=address.city,
            description=address.description,
            lat=address.lat,
            lng=address.lng,
            street=address.street,
            metro_stations=self._map_metro_stations(address.metro_stations)
        )

    def _map_metro_stations(self, stations: list[HHMetroStation] | None) -> list[MetroStation] | None:
        if not stations:
            return None
        return [
            MetroStation(
                lat=s.lat,
                lng=s.lng,
                line_id=s.line_id,
                line_name=s.line_name,
                station_name=s.station_name
            ) for s in stations
        ]
