from datetime import datetime, timedelta, time
from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, List
import enum

class Periodicity(enum.Enum):
    ONCE_A_DAY = "ежедневно"
    HOURLY = "ежечасно"

# Определяем класс для входящих данных
class ScheduleCreateRequest(BaseModel):
    drug: str = Field(..., description="Наименование лекарства")
    periodicity: Periodicity = Field(..., description="Периодичность приёмов")
    duration_days: Optional[int] = Field(None, description="Продолжительность лечения в днях (Optional)")
    user_id: int = Field(..., description="Идентификатор пациента (user_id)")
    first_time: datetime = Field(..., description="Дата и время первого приема (YYYY-MM-DD HH:MM)")

# Определяем класс ответа
class ScheduleDetailsResponse(BaseModel):
    schedule_id: int
    drug: str
    periodicity: Periodicity
    duration_days: Optional[int]
    user_id: int
    first_time: datetime
    takings: List[datetime] = []  # Список времени приемов (пустой по умолчанию)
    last_day: Optional[datetime] = None  # Последний день приема (расчетный)


    @classmethod
    def round_minute(cls, value: datetime):
        """Округляем минуты до ближайшего временного диапазона."""
        minute = value.minute
        if 1 <= minute <= 15:
            return value.replace(minute=15, second=0, microsecond=0)
        elif 16 <= minute <= 30:
            return value.replace(minute=30, second=0, microsecond=0)
        elif 31 <= minute <= 45:
            return value.replace(minute=45, second=0, microsecond=0)
        else:
            return value.replace(hour=(value.hour + 1) % 24, minute=0, second=0, microsecond=0)

    @model_validator(mode='after')
    def generate_scheduled_times(self):
        """Генерируем расписание приемов."""
        first_time_rounded = self.round_minute(self.first_time)
        takings = []

        for day in range(self.duration_days):
            current_date = first_time_rounded + timedelta(days=day)

            if self.periodicity == Periodicity.HOURLY:
                hourly_time = current_date.replace(
                    hour=8, minute=0, second=0, microsecond=0
                )
                end_time = current_date.replace(
                    hour=21, minute=45, second=0, microsecond=0
                )

                while hourly_time <= end_time:
                    takings.append(hourly_time)
                    hourly_time += timedelta(hours=1)

            elif self.periodicity == Periodicity.ONCE_A_DAY:
                takings.append(current_date)

        if takings:
            self.last_day = takings[-1]
            self.takings = sorted(takings)

        return self

class NextTakingsResponse(BaseModel):
    """
    Модель ответа для ближайших приемов лекарств.
    """
    drug: str
    taking_time: datetime

# Пример использования
schedule_details = ScheduleDetailsResponse(
    schedule_id=1,
    drug="Аспирин",
    periodicity=Periodicity.HOURLY,
    duration_days=2,
    user_id=123,
    first_time=datetime(2025, 3, 6, 12, 45),  # Пример времени
)
# Теперь takings должен содержать результаты из валидатора
print(f"График приема лекарства: {schedule_details.takings}")
print(f"Последний день приема лекарства: {schedule_details.last_day}")
print(f"Первое время: {schedule_details.first_time}")
print(f"Периодичность: {schedule_details.periodicity}")
print(f"Продолжительность (дней): {schedule_details.duration_days}")
print(f"Последний день приема: {schedule_details.last_day}")