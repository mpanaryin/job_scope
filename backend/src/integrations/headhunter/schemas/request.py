from typing import Literal

from pydantic import Field

from src.core.schemas import CustomModel


class HHAccessUserTokenParams(CustomModel):
    """Параметры получения токена пользователя"""
    client_id: str
    client_secret: str
    code: str
    redirect_uri: str
    grant_type: Literal["authorization_code"] = "authorization_code"


class HHRefreshTokenParams(CustomModel):
    """Параметры для обновления пары access и refresh токенов"""
    refresh_token: str
    grant_type: Literal["refresh_token"] = "refresh_token"


class HHAccessApplicationTokenParams(CustomModel):
    """Параметры получения нового токена приложения"""
    client_id: str
    client_secret: str
    grant_type: Literal["client_credentials"] = "client_credentials"


class HHVacancySearchParams(CustomModel):
    """
    Параметры для запроса поиска вакансий
    /dictionaries - https://api.hh.ru/openapi/redoc#tag/Obshie-spravochniki/operation/get-dictionaries
    /ares - https://api.hh.ru/openapi/redoc#tag/Obshie-spravochniki/operation/get-areas
    /metro - https://api.hh.ru/openapi/redoc#tag/Obshie-spravochniki/operation/get-metro-stations
    /professional_roles - https://api.hh.ru/openapi/redoc#tag/Obshie-spravochniki/operation/get-professional-roles-dictionary
    /industries - https://api.hh.ru/openapi/redoc#tag/Obshie-spravochniki/operation/get-industries
    """
    page: int = Field(0, ge=0, description="Номер страницы")
    per_page: int = Field(10, le=100, description="Количество элементов на странице")
    text: str | None = Field(
        None, description="Переданное значение ищется в полях вакансии, указанных в параметре search_field. "
                          "Доступен язык запросов. Специально для этого поля есть автодополнение"
    )
    search_field: list[str] | None = Field(
        None, description="Область поиска. Справочник с возможными значениями: vacancy_search_fields в /dictionaries. "
                          "По умолчанию, используются все поля. Можно указать несколько значений"
    )
    experience: list[str] | None = Field(
        None, description="Опыт работы. Необходимо передавать id из справочника experience в /dictionaries. "
                          "Можно указать несколько значений"
    )
    employment: list[str] | None = Field(
        None, description="Тип занятости. Необходимо передавать id из справочника employment в /dictionaries. "
                          "Можно указать несколько значений"
    )
    schedule: list[str] | None = Field(
        None, description="График работы. Необходимо передавать id из справочника schedule в /dictionaries. "
                          "Можно указать несколько значений")
    area: list[str] | None = Field(
        None, description="Регион. Необходимо передавать id из справочника /areas. Можно указать несколько значений"
    )
    metro: list[str] | None = Field(
        None, description="Ветка или станция метро. Необходимо передавать id из справочника /metro. "
                          "Можно указать несколько значений"
    )
    professional_role: list[str] | None = Field(
        None, description="Профессиональная область. Необходимо передавать id из справочника /professional_roles"
    )
    industry: list[str] | None = Field(
        None, description="Индустрия компании, разместившей вакансию. "
                          "Необходимо передавать id из справочника /industries. Можно указать несколько значений"
    )
    employer_id: list[str] | None = Field(None, description="Идентификатор работодателя")
    currency: str | None = Field(
        None, description="Код валюты. Справочник с возможными значениями: currency (ключ code) в /dictionaries. "
                          "Имеет смысл указывать только совместно с параметром salary"
    )
    salary: int | None = Field(None, description="Размер заработной платы")
    label: list[str] | None = Field(None, description="Фильтр по меткам вакансий")
    only_with_salary: bool = Field(False, description="Показывать вакансии только с указанной зарплатой")
    period: int | None = Field(None, description="Количество дней поиска вакансий")
    date_from: str | None = Field(None, description="Дата начала поиска (YYYY-MM-DD)")
    date_to: str | None = Field(None, description="Дата окончания поиска (YYYY-MM-DD)")
    top_lat: float | None = Field(None, description="Верхняя граница широты")
    bottom_lat: float | None = Field(None, description="Нижняя граница широты")
    left_lng: float | None = Field(None, description="Левая граница долготы")
    right_lng: float | None = Field(None, description="Правая граница долготы")
    order_by: str | None = Field(
        None, description="Сортировка списка вакансий. Справочник с возможными значениями: vacancy_search_order "
                          "в /dictionaries. Если выбрана сортировка по удалённости от гео-точки distance, "
                          "необходимо также задать её координаты: sort_point_lat, sort_point_lng"
    )
    sort_point_lat: float | None = Field(None, description="Широта точки сортировки")
    sort_point_lng: float | None = Field(None, description="Долгота точки сортировки")
    clusters: bool = Field(False, description="Возвращать ли кластеры для поиска")
    describe_arguments: bool = Field(False, description="Возвращать ли описание параметров")
    no_magic: bool = Field(False, description="Отключить автоматическое преобразование")
    premium: bool = Field(False, description="Учитывать премиум-вакансии")
    responses_count_enabled: bool = Field(False, description="Добавить количество откликов")
    part_time: list[str] | None = Field(None, description="Параметры подработки")
    accept_temporary: bool = Field(False, description="Только временная работа")
    locale: str = Field("RU", description="Локализация (RU, EN и т.д.)")
    host: str = Field("hh.ru", description="Домен (hh.ru, rabota.by и т.д.)")
