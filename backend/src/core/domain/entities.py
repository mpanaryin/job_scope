import datetime
from typing import Any
from zoneinfo import ZoneInfo

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, model_validator, Field


class CustomModel(BaseModel):
    """Custom Base pydantic model"""

    @model_validator(mode="after")
    def normalize_datetimes(self) -> "CustomModel":
        """
        Normalize all datetime fields in the model.

        - If the datetime has a timezone, it will be converted to Europe/Moscow.
        - If no timezone is present, Europe/Moscow will be assigned.
        - Microseconds will be removed.
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
        """
        Return a JSON-serializable dictionary representation of the model.

        Uses FastAPI's `jsonable_encoder` for safe serialization of complex types.
        """
        default_dict = self.model_dump()
        return jsonable_encoder(default_dict)


class BulkResult(BaseModel):
    """
    Represents the result of a bulk operation.

    Attributes:
        success (int): Number of successfully processed items.
        failed (int | list[Any]): Number of failed items or a list with failure details.
        skipped (int | None): Number of skipped items, if applicable.
        total (int | None): Total number of items processed.
        meta (dict[str, Any] | None): Optional metadata or additional context about the operation.
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
