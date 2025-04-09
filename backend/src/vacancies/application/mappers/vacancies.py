from pydantic import AnyUrl

from src.integrations.infrastructure.headhunter.contracts.response import HHVacancy
from src.integrations.domain.interfaces import TVacancy
from src.vacancies.application.mappers.helpers import HHVacancyToDomainMapper
from src.vacancies.domain.entities import Vacancy
from src.vacancies.domain.dtos import VacancySource, VacancyCreateDTO


class VacancyOriginalMapper:
    """
    Maps raw dictionary data to typed external API vacancy models.

    Attributes:
        source (VacancySource): The source of the external vacancy data (e.g., HeadHunter).
    """

    def __init__(self, source: VacancySource):
        self.source = source

    def map(self, vacancies: list[dict]) -> list[TVacancy]:
        """
        Convert a list of raw vacancy dictionaries into typed TVacancy models.

        :param vacancies: List of vacancy dictionaries.
        :return: List of TVacancy instances.
        """
        return [self._map_vacancy_to_original(vacancy) for vacancy in vacancies]

    def map_one(self, vacancy: dict) -> TVacancy:
        """
        Convert a single vacancy dictionary into a typed TVacancy model.

        :param vacancy: Vacancy dictionary.
        :return: TVacancy instance.
        """
        return self._map_vacancy_to_original(vacancy)

    def _map_vacancy_to_original(self, vacancy: dict) -> TVacancy:
        """
        Internal mapping of a dictionary to a TVacancy model.

        :param vacancy: Raw dictionary.
        :return: Parsed TVacancy model.
        """
        if isinstance(vacancy, dict):
            if self.source == VacancySource.HEADHUNTER:
                return HHVacancy.model_validate(vacancy)
        raise TypeError(f"Vacancy with type dict and source {self.source} cant be parsed into a TVacancy")


class VacancyAPIToDomainMapper:
    """
    Maps API-level vacancy data to internal domain models.

    Attributes:
        source (VacancySource | None): Optional explicit source type.
    """

    def __init__(self, vacancy_source: VacancySource | None = None):
        self.source = vacancy_source

    def map(self, vacancies: list[TVacancy | dict]) -> list[Vacancy]:
        """
        Convert a list of external vacancies (TVacancy or raw dicts) to domain models.

        :param vacancies: List of external vacancy representations.
        :return: List of domain vacancy models.
        """
        self.source = self._set_vacancy_source(vacancies, self.source)
        return [self._map_vacancy_to_domain(vacancy) for vacancy in vacancies]

    def map_one(self, vacancy: TVacancy | dict) -> Vacancy:
        """
        Convert a single external vacancy to a domain model.

        :param vacancy: TVacancy or raw dictionary.
        :return: Domain Vacancy instance.
        """
        self.source = self._set_vacancy_source([vacancy], self.source)
        return self._map_vacancy_to_domain(vacancy)

    def _map_vacancy_to_domain(self, vacancy: TVacancy | dict) -> Vacancy:
        """
        Internal mapping from TVacancy to Vacancy.

        :param vacancy: TVacancy or dict.
        :return: Mapped Vacancy.
        """
        if isinstance(vacancy, dict):
            vacancy = VacancyOriginalMapper(self.source).map_one(vacancy)

        if self.source == VacancySource.HEADHUNTER:
            return HHVacancyToDomainMapper().map(vacancy, self.source)

    def _set_vacancy_source(self, vacancies: list[TVacancy], source: VacancySource | None):
        """
        Determine or validate the vacancy source.

        :param vacancies: Input vacancy data.
        :param source: Optional pre-defined source.
        :return: Finalized source.
        """
        if source:
            return source

        if vacancies:
            if isinstance(vacancies[0], HHVacancy):
                return VacancySource.HEADHUNTER

        raise TypeError('Invalid vacancies: source cannot be determined')


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


class VacancyDomainToElasticMapper:
    """
    Maps internal domain vacancy models to Elasticsearch-compatible document structures.
    """

    def map(self, vacancies: list[Vacancy]) -> list[dict]:
        """
        Convert domain vacancies to Elasticsearch documents.

        :param vacancies: List of domain model vacancies.
        :return: List of documents with metadata for bulk indexing.
        """
        return [self.map_one(vacancy) for vacancy in vacancies]

    def map_one(self, vacancy: Vacancy) -> dict:
        """
        Convert a single domain vacancy to Elasticsearch document format.

        :param vacancy: Domain model vacancy.
        :return: Elasticsearch-compatible document.
        """
        doc = self._map_vacancy_to_document(vacancy)
        return {
            "_op_type": "index",
            "_index": "vacancies",
            "_id": doc["id"],
            "_source": doc,
        }

    def _map_vacancy_to_document(self, vacancy: Vacancy) -> dict:
        """
        Convert domain vacancy to document body for Elasticsearch.

        :param vacancy: Domain model.
        :return: Mapped document dictionary.
        """
        return {
            "id": f"{vacancy.source_name}{vacancy.source_id}",
            "source": {
                "id": vacancy.source_id,
                "name": str(vacancy.source_name),
            },
            "name": vacancy.name,
            "url": vacancy.alternate_url,
            "description": vacancy.description,
            "area": {
                "name": vacancy.area.name,
                "url": vacancy.area.url
            } if vacancy.area else None,
            "address": {
                "city": vacancy.address.city,
                "street": vacancy.address.street,
                "building": vacancy.address.building,
                "raw": f"{vacancy.address.city}, {vacancy.address.street}, {vacancy.address.building}",
                "lat": vacancy.address.lat,
                "lng": vacancy.address.lng
            } if vacancy.address else None,
            "employer": {
                "name": vacancy.employer.name,
                "trusted": vacancy.employer.trusted,
                "url": vacancy.employer.url
            } if vacancy.employer else None,
            "salary": {
                "currency": vacancy.salary.currency,
                "from": vacancy.salary.from_,
                "to": vacancy.salary.to,
                "gross": vacancy.salary.gross
            } if vacancy.salary else None,
            "experience": {
                "name": vacancy.experience.name
            } if vacancy.experience else None,
            "employment": {
                "name": vacancy.employment.name
            } if vacancy.employment else None,
            "schedule": {
                "name": vacancy.schedule.name
            } if vacancy.schedule else None,
            "snippet": {
                "requirement": vacancy.requirement,
                "responsibility": vacancy.responsibility
            },
            "has_test": vacancy.has_test,
            "is_archived": vacancy.archived,
            "published_at": vacancy.published_at,
            "created_at": vacancy.created_at
        }
