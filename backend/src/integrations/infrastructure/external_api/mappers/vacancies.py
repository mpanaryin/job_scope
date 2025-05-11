from src.integrations.infrastructure.external_api.headhunter.schemas.response import HHVacancy
from src.integrations.infrastructure.external_api.mappers.helpers import HHVacancyToDomainMapper
from src.vacancies.domain.entities import VacancySource, Vacancy
from src.vacancies.domain.interfaces.vacancy_source_client import TVacancy


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


class VacancyExternalToDomainMapper:
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
