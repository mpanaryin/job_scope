from pydantic import AnyUrl

from src.integrations.headhunter.schemas.response import VacancyItem
from src.vacancies.schemas import VacancyCreate, VacancySource


def map_hh_vacancy_to_domain_vacancy(vacancy: VacancyItem) -> VacancyCreate:
    """Маппинг VacancyItem (ответ от внешнего API) к VacancyCreate (схема для создания в БД)"""
    return VacancyCreate(
        source_name=VacancySource.HEADHUNTER,
        source_id=int(vacancy.id),
        url=AnyUrl(vacancy.alternate_url),
        name=vacancy.name,
        description=_get_description(vacancy),
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


def map_hh_vacancies_to_domain_vacancies(vacancies: list[VacancyItem]) -> list[VacancyCreate]:
    """Маппинг списка VacancyItem к списку VacancyCreate"""
    return [map_hh_vacancy_to_domain_vacancy(vacancy) for vacancy in vacancies]


def map_hh_vacancy_to_elastic_vacancy(vacancy: VacancyItem) -> dict:
    """Маппинг VacancyItem к формату индекса ElasticSearch для вакансий"""
    return {
        "id": f"headhunter_{vacancy.id}",
        "source": {
            "id": vacancy.id,
            "name": "headhunter",
        },
        "name": vacancy.name,
        "url": vacancy.alternate_url,
        "description": _get_description(vacancy),
        "area": {
            "id": vacancy.area.id,
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
            "id": vacancy.employer.id,
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
            "id": vacancy.experience.id,
            "name": vacancy.experience.name
        } if vacancy.experience else None,
        "employment": {
            "id": vacancy.employment.id,
            "name": vacancy.employment.name
        } if vacancy.employment else None,
        "schedule": {
            "id": vacancy.schedule.id,
            "name": vacancy.schedule.name
        } if vacancy.schedule else None,
        "snippet": {
            "requirement": vacancy.snippet.requirement,
            "responsibility": vacancy.snippet.responsibility
        } if vacancy.snippet else None,
        "has_test": vacancy.has_test,
        "is_archived": vacancy.archived,
        "published_at": vacancy.published_at,
        "created_at": vacancy.created_at
    }


def map_hh_vacancies_to_elastic_vacancies(vacancies: list[VacancyItem]):
    """Маппинг списка VacancyItem к списку dict, который соответствует индексу в ElasticSearch"""
    es_vacancies = []
    for vacancy in vacancies:
        doc = map_hh_vacancy_to_elastic_vacancy(vacancy)
        es_vacancies.append({
            "_op_type": "index",
            "_index": "vacancies",
            "_id": doc["id"],
            "_source": doc,
        })
    return es_vacancies


def _get_description(vacancy: VacancyItem) -> str | None:
    """Вспомогательная функция для получения описания по вакансии"""
    description = None
    if vacancy.snippet:
        requirement = vacancy.snippet.requirement or ''
        responsibility = vacancy.snippet.responsibility or ''
        description = f"{requirement}\n\n{responsibility}".strip()
    return description
