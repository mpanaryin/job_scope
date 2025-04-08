from pydantic import AnyUrl

from src.integrations.infrastructure.headhunter.contracts.response import HHVacancy
from src.integrations.domain.interfaces import TVacancy
from src.vacancies.application.mappers.helpers import HHVacancyToDomainMapper
from src.vacancies.domain.entities import Vacancy
from src.vacancies.domain.dtos import VacancySource, VacancyCreateDTO


class VacancyOriginalMapper:
    """
    Преобразует dict в оригинальный тип вакансии
    Например, может использоваться для преобразования meta данных вакансий
    """

    def __init__(self, source: VacancySource):
        self.source = source

    def map(self, vacancies: list[dict]) -> list[TVacancy]:
        return [self._map_vacancy_to_original(vacancy) for vacancy in vacancies]

    def map_one(self, vacancy: dict) -> TVacancy:
        return self._map_vacancy_to_original(vacancy)

    def _map_vacancy_to_original(self, vacancy: dict) -> TVacancy:
        """Преобразует dict формат вакансии в оригинальный её тип"""
        if isinstance(vacancy, dict):
            if self.source == VacancySource.HEADHUNTER:
                return HHVacancy.model_validate(vacancy)
        raise TypeError(f"Vacancy with type dict and source {self.source} cant be parsed into a TVacancy")


class VacancyAPIToDomainMapper:
    """Преобразует TVacancy или ей подобный dict к доменной модели"""

    def __init__(self, vacancy_source: VacancySource | None = None):
        self.source = vacancy_source

    def map(self, vacancies: list[TVacancy | dict]) -> list[Vacancy]:
        """Маппинг списка TVacancy к списку VacancyCreate"""
        self.source = self._set_vacancy_source(vacancies, self.source)
        return [self._map_vacancy_to_domain(vacancy) for vacancy in vacancies]

    def map_one(self, vacancy: TVacancy | dict) -> Vacancy:
        self.source = self._set_vacancy_source([vacancy], self.source)
        return self._map_vacancy_to_domain(vacancy)

    def _map_vacancy_to_domain(self, vacancy: TVacancy | dict) -> Vacancy:
        """Маппинг TVacancy (ответ от внешнего API) к VacancyCreate (схема для создания в БД)"""
        if isinstance(vacancy, dict):
            vacancy = VacancyOriginalMapper(self.source).map_one(vacancy)

        if self.source == VacancySource.HEADHUNTER:
            return HHVacancyToDomainMapper().map(vacancy, self.source)

    def _set_vacancy_source(self, vacancies: list[TVacancy], source: VacancySource | None):
        """Устанавливаем источник вакансий"""
        if source:
            return source

        if vacancies:
            if isinstance(vacancies[0], HHVacancy):
                return VacancySource.HEADHUNTER

        raise TypeError('Invalid vacancies: source cannot be determined')


class VacancyDomainToDTOMapper:
    """Преобразует доменную модель к модели базы данных"""
    def map(self, vacancies: list[Vacancy]) -> list[VacancyCreateDTO]:
        """Маппинг списка TVacancy к списку VacancyCreate"""
        return [self._map_domain_vacancy_to_db_schema(vacancy) for vacancy in vacancies]

    def map_one(self, vacancy: Vacancy) -> VacancyCreateDTO:
        return self._map_domain_vacancy_to_db_schema(vacancy)

    def _map_domain_vacancy_to_db_schema(self, vacancy: Vacancy) -> VacancyCreateDTO:
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
    """Преобразует доменную модель к модели elastic search"""

    def map(self, vacancies: list[Vacancy]) -> list[dict]:
        """Маппинг списка вакансий к формату документа поисковой базы данных"""
        return [self.map_one(vacancy) for vacancy in vacancies]

    def map_one(self, vacancy: Vacancy) -> dict:
        """Маппинг вакансии к формату документа поисковой базы данных"""
        doc = self._map_vacancy_to_document(vacancy)
        return {
            "_op_type": "index",
            "_index": "vacancies",
            "_id": doc["id"],
            "_source": doc,
        }

    def _map_vacancy_to_document(self, vacancy: Vacancy) -> dict:
        """Маппинг вакансии к формату документа поисковой базы данных"""
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
