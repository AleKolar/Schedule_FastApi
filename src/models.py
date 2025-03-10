from datetime import datetime, timedelta
from typing import List, Optional
import importlib

from pydantic import BaseModel, Field, model_validator, ConfigDict



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
    first_time: datetime = Field(..., description="Дата и время первого приема (YYYY-MM-DD HH:MM)")
    drugs: List[Drug] = Field(..., description="Список назначенных лекарств")
    takings: List[List[datetime]] = []
    last_day_times: List[Optional[datetime]] = []

    class ModX:
        def __init__(self):
            m2 = importlib.import_module('UserRepository')
            self.mod_obj = m2.ModY()

        @model_validator(mode='after')
        def generate_scheduled_times(self, user):
            user.takings, user.last_day_times = self.mod_obj.generate_scheduled_times(user)
            return user

class SchemaUser(User):
    id: int
    model_config = ConfigDict(from_attributes=True)
