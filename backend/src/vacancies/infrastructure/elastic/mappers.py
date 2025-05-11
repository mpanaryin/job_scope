from src.vacancies.domain.entities import Vacancy


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