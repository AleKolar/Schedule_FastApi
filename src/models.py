from __future__ import annotations

import uuid
from datetime import datetime, timedelta
from typing import List, Optional, Union

from pydantic import BaseModel, Field, model_validator, ConfigDict

from src.repository.utils import ScheduleGeneratorTimes


class Drug(BaseModel):
    drug: str = Field(..., description="Наименование лекарства")
    periodicity: int = Field(..., gt=0, description="Периодичность приёмов в часах")
    duration_days: Optional[int] = Field(None, ge=1, description="Продолжительность лечения в днях (Optional)")

    @property
    def is_continuous(self) -> bool:
        return self.duration_days is None  # если None - лекарство принимается постоянно


class SchemaDrug(Drug):
    id: int = Field(..., description="Идентификатор лекарства в базе данных")
    user_id: uuid.UUID = Field(..., description="Идентификатор пользователя, которому назначено лекарство")
    model_config = ConfigDict(from_attributes=True)


class User(BaseModel):
    user_id: uuid.UUID = Field(..., description="Идентификатор пациента (user_id)")
    schedule: List[List[Union[str, datetime, None]]] = []
    last_day_times: List[Optional[datetime]] = Field(..., description="Последние дни приема лекарств")
    drugs: List[str] = Field(..., description="Список лекарств пациента")

    @model_validator(mode='after')
    def generate_scheduled_times(self):
        self.schedule, self.last_day_times = ScheduleGeneratorTimes.generate_scheduled_times(self)
        return self

class SchemaUser(User):
    model_config = ConfigDict(from_attributes=True)

class ScheduleCreate(BaseModel):
    first_time: datetime = Field(..., description="Дата и время начала приема лекарства")
    drug: str = Field(..., description="Наименование лекарства")
    periodicity: int = Field(..., gt=0, description="Периодичность приёмов в часах")
    duration_days: Optional[int] = Field(None, ge=1, description="Продолжительность лечения в днях (Optional)")
    user_id: uuid.UUID = Field(..., description="Идентификатор пациента (user_id)")
    schedule_id: int = Field(..., description="Идентификатор расписания (schedule_id)")


class SchemaScheduleCreate(ScheduleCreate):
    model_config = ConfigDict(from_attributes=True)


