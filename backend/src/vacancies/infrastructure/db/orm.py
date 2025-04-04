import datetime
import uuid

import uuid6

from sqlalchemy import UUID, String, Integer, Text, Boolean, DateTime, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from src.db.base import Base
from src.utils.datetimes import get_timezone_now
from src.vacancies.domain.schemas import VacancySource


class Vacancy(Base):
    __tablename__ = 'vacancies'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid6.uuid6
    )
    # Источник вакансии
    source_name: Mapped[VacancySource] = mapped_column(String(length=30), nullable=False, index=True)
    source_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    url: Mapped[str] = mapped_column(String(length=2048), nullable=False)
    # Название вакансии
    name: Mapped[str] = mapped_column(String(length=100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Зарплата
    salary_from: Mapped[int | None] = mapped_column(Integer, nullable=True)
    salary_to: Mapped[int | None] = mapped_column(Integer, nullable=True)
    salary_currency: Mapped[str | None] = mapped_column(String(length=5), nullable=True)
    salary_gross: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    # Данные по работодателю
    area_name: Mapped[str | None] = mapped_column(String(length=256), nullable=True)
    employer_name: Mapped[str | None] = mapped_column(String(length=512), nullable=True)
    # Требования к вакансии
    employment: Mapped[str | None] = mapped_column(String(length=50), nullable=True)
    experience: Mapped[str | None] = mapped_column(String(length=50), nullable=True)
    schedule: Mapped[str | None] = mapped_column(String(length=50), nullable=True)
    has_test: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    # Дополнительная информация
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False, index=True, nullable=False)
    type: Mapped[str | None] = mapped_column(String(length=100), nullable=True)
    meta: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    # Даты
    published_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), default=get_timezone_now, index=True
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), default=get_timezone_now, onupdate=get_timezone_now, nullable=False
    )

    __table_args__ = (
        UniqueConstraint('source_name', 'source_id', name='uq_vacancy_source'),
    )
