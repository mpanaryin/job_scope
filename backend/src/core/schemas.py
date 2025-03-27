import datetime
from zoneinfo import ZoneInfo

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, model_validator


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
