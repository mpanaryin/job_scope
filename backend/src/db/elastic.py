from elasticsearch import AsyncElasticsearch

from src.core.config import settings

# Подключение к Elasticsearch
es_client = AsyncElasticsearch(settings.ELASTICSEARCH_HOSTS)


async def create_index():
    """Создаёт индекс 'vacancies'"""
    index_body = {
        "mappings": {
            "properties": {
                "id": {"type": "keyword"},
                "title": {"type": "text", "analyzer": "russian"},
                "salary": {"type": "integer"},
                "company": {"type": "text"},
                "location": {"type": "keyword"},
                "published_at": {"type": "date"}
            }
        }
    }
    result = await es_client.indices.create(index="vacancies", body=index_body, ignore=400)  # ignore=400 -> не создаст, если индекс уже есть
    return result


async def add_vacancy():
    """Добавляем вакансию в Elasticsearch"""
    vacancy = {
        "id": "12345",
        "title": "Python Developer",
        "salary": 150000,
        "company": "Google",
        "location": "Москва",
        "published_at": "2025-03-18T12:00:00"
    }
    result = await es_client.index(index="vacancies", id=vacancy["id"], body=vacancy)
    return result


async def get_vacancy(vacancy_id: str):
    """Получаем вакансию по ID"""
    response = await es_client.get(index="vacancies", id=vacancy_id, ignore=404)
    return response["_source"] if response.get("found") else {"message": "Vacancy not found"}


async def search_vacancies(query: str, min_salary: int | None = None):
    """Поиск вакансий"""
    search_query = {
        "query": {
            "bool": {
                "must": [{"match": {"title": query}}],
                "filter": []
            }
        }
    }

    if min_salary:
        search_query["query"]["bool"]["filter"].append({"range": {"salary": {"gte": min_salary}}})

    response = await es_client.search(index="vacancies", body=search_query)
    return response["hits"]["hits"]


async def update_vacancy(vacancy_id: str, new_salary: int):
    """Обновляем зарплату у вакансии"""
    result = await es_client.update(index="vacancies", id=vacancy_id, body={
        "doc": {"salary": new_salary}
    })
    return result


async def delete_vacancy(vacancy_id: str):
    """Удаляем вакансию по ID"""
    result = await es_client.delete(index="vacancies", id=vacancy_id, ignore=[400, 404])
    return result


async def delete_index():
    """Удаляет индекс 'vacancies'"""
    result = await es_client.indices.delete_by_pk(index="vacancies", ignore=[400, 404])
    return result
