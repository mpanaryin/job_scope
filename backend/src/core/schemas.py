import datetime
from typing import Any
from zoneinfo import ZoneInfo

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, model_validator, Field


class CustomModel(BaseModel):
    @model_validator(mode="after")
    def normalize_datetimes(self) -> "CustomModel":
        """
        Общая обработка datetime:
        - если есть таймзона, привести к Europe/Moscow
        - если нет — установить таймзону Moscow
        - убрать микросекунды
        """
        tz_moscow = ZoneInfo("Europe/Moscow")

        for field_name, value in self.__dict__.items():
            if isinstance(value, datetime.datetime):
                if value.tzinfo:
                    value = value.astimezone(tz_moscow)
                else:
                    value = value.replace(tzinfo=tz_moscow)
                value = value.replace(microsecond=0)
                setattr(self, field_name, value)

        return self

    def serializable_dict(self, **kwargs):
        """Возвращает словарь, содержащий только сериализуемые поля."""
        default_dict = self.model_dump()
        return jsonable_encoder(default_dict)


class BulkResult(BaseModel):
    """
    Результат bulk-операции
    Attributes:
        success (int): Количество успешно обработанных записей
        failed (int | list[Any]): Количество неудачных записей или список с деталями
        skipped (int | None): Количество пропущенных записей, если применимо
        total (int | None): Общее количество обработанных записей
        meta (dict[str, Any] | None): Дополнительная информация по выполненной операции
    """
    success: int = Field(..., description="Количество успешно обработанных записей")
    failed: int | list[Any] = Field(
        default=0,
        description="Количество неудачных записей или список с деталями",
    )
    skipped: int | None = Field(
        default=None,
        description="Количество пропущенных записей, если применимо"
    )
    total: int | None = Field(
        default=None,
        description="Общее количество обработанных записей"
    )
    meta: dict[str, Any] | None = Field(
        default=None,
        description="Дополнительная информация по выполненной операции"
    )
