import asyncio
import math
import os

from src.core.config import settings
from src.integrations.api_client import AuthType, APIClient
from src.integrations.headhunter.schemas import request as request_schemas
from src.integrations.headhunter.schemas import response as response_schemas


class HeadHunterService(APIClient):
    """Сервис для работы с HeadHunter API"""
    def __init__(
        self,
        source_url: str | None = 'https://api.hh.ru',
        auth_type=AuthType.BEARER_TOKEN,
        token=os.environ.get("HEADHUNTER_TOKEN")
    ):
        super(HeadHunterService, self).__init__(source_url, auth_type=auth_type, token=token)

    async def get_access_token(self) -> dict:
        """
        Получить авторизационный токен, который в дальнейшем используем для запросов
        """
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        request_data = request_schemas.AccessApplicationTokenParams(
            client_id=os.environ.get("HEADHUNTER_CLIENT_ID"),
            client_secret=os.environ.get("HEADHUNTER_CLIENT_SECRET"),
        )
        response = await self.request(
            method="POST", endpoint="/token", headers=headers,
            params=request_data.model_dump(mode="json")
        )
        result = await response.json()
        return result

    async def get_application_info(self) -> dict:
        """
        Получить информацию о текущем приложении
        """
        headers = {"HH-User-Agent": f"JobScope/1.0 {settings.EMAIL_FROM}"}
        response = await self.request(method='GET', endpoint='/me', headers=headers)
        result = await response.json()
        return result

    async def get_vacancies(
        self,
        search_params: request_schemas.VacancySearchParams
    ) -> response_schemas.VacancyResponse:
        """
        Получить вакансии HeadHunter согласно search_params
        """
        headers = {"HH-User-Agent": f"JobScope/1.0 {settings.EMAIL_FROM}"}
        response = await self.request(
            method='GET', endpoint='/vacancies', headers=headers,
            params=search_params.model_dump(mode="json", exclude_none=True, exclude_unset=True)
        )
        result = await response.json()
        return response_schemas.VacancyResponse.model_validate(result)

    async def get_all_vacancies(
        self, search_params: request_schemas.VacancySearchParams
    ) -> list[response_schemas.VacancyItem]:
        """
        Получить все вакансии по текущим параметрам.

        Текущий запрос может понадобиться, если есть потребность получить более 100 вакансий за раз.
        Есть ограничение в API на глубину более чем 2000 объектов.
        """
        # Получаем общее количество вакансий
        search_params.page = 0
        search_params.per_page = 1
        vacancy_response = await self.get_vacancies(search_params)
        # Вычисляем количество страниц
        max_pages = math.ceil(vacancy_response.found / 100)
        # Получаем все страницы отдельно
        vacancies: list[response_schemas.VacancyItem] = []
        search_params.per_page = 100
        for i in range(max_pages):
            search_params.page = i
            vacancy_response = await hh_service.get_vacancies(search_params)
            if vacancy_response.items:
                vacancies.extend(vacancy_response.items)
            # Задержку поставил на всякий случай, так как не знаю ограничений API и не хочу спамить
            await asyncio.sleep(1)
        return vacancies


hh_service = HeadHunterService()
