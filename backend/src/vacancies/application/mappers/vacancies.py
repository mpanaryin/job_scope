from pydantic import AnyUrl

from src.vacancies.domain.entities import Vacancy
from src.vacancies.domain.dtos import VacancyCreateDTO


class VacancyDomainToDTOMapper:
    """
    Maps internal domain models to DTOs for database persistence.
    """

    def map(self, vacancies: list[Vacancy]) -> list[VacancyCreateDTO]:
        """
        Convert domain vacancies to database-ready DTOs.

        :param vacancies: List of domain model vacancies.
        :return: List of DTOs ready for storage.
        """
        return [self._map_domain_vacancy_to_db_schema(vacancy) for vacancy in vacancies]

    def map_one(self, vacancy: Vacancy) -> VacancyCreateDTO:
        """
        Convert a single domain vacancy to DTO.

        :param vacancy: Domain vacancy.
        :return: VacancyCreateDTO.
        """
        return self._map_domain_vacancy_to_db_schema(vacancy)

    def _map_domain_vacancy_to_db_schema(self, vacancy: Vacancy) -> VacancyCreateDTO:
        """
        Internal mapping to DB DTO.

        :param vacancy: Domain model.
        :return: DTO for DB insertion.
        """
        return VacancyCreateDTO(
            source_name=vacancy.source_name,
            source_id=int(vacancy.source_id),
            url=AnyUrl(vacancy.alternate_url),
            name=vacancy.name,
            description=vacancy.description,
            salary_from=vacancy.salary.from_ if vacancy.salary else None,
            salary_to=vacancy.salary.to if vacancy.salary else None,
            salary_currency=vacancy.salary.currency if vacancy.salary else None,
            salary_gross=vacancy.salary.gross if vacancy.salary else None,
            published_at=vacancy.published_at,
            created_at=vacancy.created_at,
            area_name=vacancy.area.name if vacancy.area else None,
            employer_name=vacancy.employer.name if vacancy.employer else None,
            employment=vacancy.employment.name if vacancy.employment else None,
            experience=vacancy.experience.name if vacancy.experience else None,
            schedule=vacancy.schedule.name if vacancy.schedule else None,
            has_test=vacancy.has_test,
            is_archived=vacancy.archived,
            type=vacancy.type.name if vacancy.type else None,
            meta=vacancy.model_dump(mode="json")
        )
