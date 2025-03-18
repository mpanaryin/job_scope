from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, ConfigDict, model_validator


def convert_datetime_to_gmt(dt: datetime) -> str:
    if not dt.tzinfo:
        dt = dt.replace(tzinfo=ZoneInfo("Europe/Moscow"))

    return dt.strftime("%Y-%m-%dT%H:%M:%S%z")


class CustomModel(BaseModel):
    model_config = ConfigDict(
        json_encoders={datetime: convert_datetime_to_gmt},
        populate_by_name=True,
    )

    @model_validator(mode="before")
    @classmethod
    def set_null_microseconds(cls, data: dict[str, Any]) -> dict[str, Any] | bytes:
        # Дополнительная проверка, так как сюда orm объекты попадают
        if not isinstance(data, dict):
            if isinstance(data, bytes):
                return data
            data = data.__dict__
        datetime_fields = {
            k: v.replace(microsecond=0)
            for k, v in data.items()
            if isinstance(v, datetime)
        }
        return {**data, **datetime_fields}

    def serializable_dict(self, **kwargs):
        """Return a dict which contains only serializable fields."""
        default_dict = self.model_dump()
        return jsonable_encoder(default_dict)
