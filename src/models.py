import uuid
from datetime import datetime, timedelta
from typing import List, Optional
import importlib

from pydantic import BaseModel, Field, model_validator, ConfigDict
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import UUID

from src.repository.utils import ScheduleGenerator


class Drug(BaseModel):
    drug: str = Field(..., description="Наименование лекарства")
    periodicity: int = Field(..., gt=0,description="Периодичность приёмов в часах")
    duration_days: Optional[int] = Field(None, ge=1,description="Продолжительность лечения в днях (Optional)")

    @property
    def is_continuous(self) -> bool:
        return self.duration_days is None # если None - лекарство принимается постоянно

class SchemaDrug(Drug):
    id: int
    model_config = ConfigDict(from_attributes=True)

class User(BaseModel):
    user_id: int = Field(..., description="Идентификатор пациента (user_id)")
    drugs: List[Drug] = Field(..., description="Список назначенных лекарств")
    first_time: datetime = Field(..., description="Дата и время первого приема (YYYY-MM-DD HH:MM)")
    schedule: List[List[datetime]] = []
    last_day_times: List[Optional[datetime]] = []

    @model_validator(mode='after')
    def generate_scheduled_times(self):
        self.schedule, self.last_day_times = ScheduleGenerator.generate_scheduled_times(self.drugs, self.first_time)
        return self


class ScheduleRequest(BaseModel):
    id: int = Field(..., description="Идентификатор расписания")
    first_time: datetime = Field(..., description="Дата и время первого приема (YYYY-MM-DD HH:MM)")
    drug: str = Field(..., description="Наименование лекарства")
    periodicity: int = Field(..., gt=0, description="Периодичность приёмов в часах")
    duration_days: Optional[int] = Field(None, ge=1, description="Продолжительность лечения в днях (Optional)")

class SchemaScheduleRequest(ScheduleRequest):
    model_config = ConfigDict(from_attributes=True)

class ScheduleCreate(BaseModel):
    first_time: datetime
    drug: str
    periodicity: int
    duration_days: Optional[int]
    user_id: uuid.UUID

class SchemaScheduleCreate(ScheduleRequest):
    model_config = ConfigDict(from_attributes=True)


