import asyncio
import math
import os

from src.core.config import settings
from src.integrations.infrastructure.http.interfaces import IAsyncHttpClient
from src.integrations.infrastructure.http.services.api_client import AuthType, APIClientService
from src.integrations.infrastructure.external_api.headhunter.schemas.request import (
    HHAccessApplicationTokenParams,
    HHVacancySearchParams
)
from src.integrations.infrastructure.external_api.headhunter.schemas.response import HHVacancyResponse, HHVacancy
from src.integrations.infrastructure.http.aiohttp_client import AiohttpClient
from src.integrations.infrastructure.external_api.mappers.vacancies import VacancyExternalToDomainMapper
from src.vacancies.domain.entities import Vacancy
from src.vacancies.domain.interfaces.vacancy_source_client import IVacancySourceClient


class HeadHunterAdapter(
    APIClientService,
    IVacancySourceClient[HHVacancySearchParams, HHVacancy, HHVacancyResponse]
):
    """
    Adapter for interacting with the HeadHunter public API.

    This adapter implements the `IVacancySourceClient` interface and provides
    an abstraction over key endpoints such as:
    - Access token retrieval
    - Application information
    - Vacancy search (single-page or full pagination)

    Args:
        client (IAsyncHttpClient): An async HTTP client (default: AiohttpClient).
        source_url (str): Base API URL (default: "https://api.hh.ru").
        auth_type (AuthType): Authorization type to use (default: Bearer).
        token (str | None): Optional token to include in requests.
    """
    def __init__(
        self,
        client: IAsyncHttpClient = AiohttpClient,
        source_url: str = 'https://api.hh.ru',
        auth_type: AuthType = AuthType.BEARER_TOKEN,
        token: str | None = os.environ.get("HEADHUNTER_TOKEN")
    ):
        super(HeadHunterAdapter, self).__init__(client=client, source_url=source_url, auth_type=auth_type, token=token)

    async def get_access_token(self) -> dict:
        """
        Retrieve an application-level access token from HeadHunter.

        :return dict: Token information including `access_token`, `expires_in`, etc.
        """
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        request_data = HHAccessApplicationTokenParams(
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
        Fetch information about the currently authorized HeadHunter application.

        Requires an access token.

        :return dict: Metadata about the registered application.
        """
        headers = {"HH-User-Agent": f"JobScope/1.0 {settings.EMAIL_FROM}"}
        response = await self.request(method='GET', endpoint='/me', headers=headers)
        result = await response.json()
        return result

    async def get_vacancies(
        self, search_params: HHVacancySearchParams
    ) -> list[Vacancy]:
        """
        Perform a single-page vacancy search using the given query parameters.

        :param search_params: Parameters to filter the search.
        :return list[Vacancy]: A list of matching vacancies.
        """
        vacancy_response = await self._get_vacancy_response(search_params)
        return VacancyExternalToDomainMapper().map(vacancy_response.items)

    async def get_all_vacancies(
        self, search_params: HHVacancySearchParams
    ) -> list[Vacancy]:
        """
        Retrieve all vacancies matching the provided search parameters.

        This method handles pagination automatically and is useful when a full
        data set is needed.
        Note that the HeadHunter API may have internal
        pagination limits (e.g., 2000 records), which can affect the result.

        :param search_params: Query parameters for the search.
        :return list[Vacancy]: A complete list of matching vacancies.
        """
        # Get the total number of vacancies
        search_params.page = 0
        search_params.per_page = 1

        vacancy_response = await self._get_vacancy_response(search_params)
        # Calculate the number of pages
        max_pages = math.ceil(vacancy_response.found / 100)
        # Fetch all pages separately
        vacancies: list[HHVacancy] = []
        search_params.per_page = 100
        for page_num in range(max_pages):
            search_params.page = page_num
            _vacancy_response = await self._get_vacancy_response(search_params)
            if _vacancy_response.items:
                vacancies.extend(_vacancy_response.items)
            # Added a delay just in case, since the API rate limits are unknown and I want to avoid spamming.
            await asyncio.sleep(1)
        return VacancyExternalToDomainMapper().map(vacancies)

    async def _get_vacancy_response(self, search_params: HHVacancySearchParams) -> HHVacancyResponse:
        """
        Internal helper to retrieve the full vacancy response payload from the API.

        This includes pagination metadata, cluster information, and the list of
        vacancy items, all wrapped in a validated `HHVacancyResponse`.

        :param search_params: Query parameters for the request.
        :return HHVacancyResponse: Validated response with vacancy items and metadata.
        """
        headers = {"HH-User-Agent": f"JobScope/1.0 {settings.EMAIL_FROM}"}
        response = await self.request(
            method='GET', endpoint='/vacancies', headers=headers,
            params=search_params.model_dump(mode="json", exclude_none=True, exclude_unset=True)
        )
        result = await response.json()
        return HHVacancyResponse.model_validate(result)
