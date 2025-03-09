from datetime import datetime, timedelta
from typing import List, Optional

from pydantic import BaseModel, Field, model_validator


class Drug(BaseModel):
    drug: str = Field(..., description="Наименование лекарства")
    periodicity: int = Field(..., description="Периодичность приёмов в часах")
    duration_days: Optional[int] = Field(None, description="Продолжительность лечения в днях (Optional)")


class User(BaseModel):
    user_id: int = Field(..., description="Идентификатор пациента (user_id)")
    first_time: datetime = Field(..., description="Дата и время первого приема (YYYY-MM-DD HH:MM)")
    drugs: List[Drug] = Field(..., description="Список назначенных лекарств")
    takings: List[List[datetime]] = []
    last_day_times: List[Optional[datetime]] = []

    @classmethod
    def round_minute(cls, value: datetime):
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
        self.takings = []
        self.last_day_times = []

        for drug in self.drugs:
            first_time_rounded = self.round_minute(self.first_time)
            takings = []

            # Генерируем расписание
            for day in range(drug.duration_days):
                current_date = first_time_rounded.date() + timedelta(days=day)

                # Устанавливаем начальное время для текущего дня
                if day == 0:
                    schedule_time = first_time_rounded
                else:
                    schedule_time = datetime.combine(current_date, datetime.min.time()).replace(hour=8)  # Начинаем с 8:00

                # Конечное время приема на последний день
                end_time_day = datetime.combine(current_date, datetime.min.time()).replace(hour=22)

                # Добавляем приемы
                while schedule_time < end_time_day:
                    if schedule_time.hour >= 8 and schedule_time < end_time_day:
                        takings.append(schedule_time)

                    # Увеличиваем текущее время приема на периодичность
                    schedule_time += timedelta(hours=drug.periodicity)

            self.takings.append(takings)

            # Определяем время окончания лечения, вычитая периодичность
            if takings:
                last_drug_time = first_time_rounded + timedelta(days=drug.duration_days)  # Время окончания лечения
                last_drug_time -= timedelta(hours=drug.periodicity)  # Вычитаем периодичность
                self.last_day_times.append(last_drug_time)
            else:
                self.last_day_times.append(None)

        return self

    def get_next_taking(self, drug_index: int) -> Optional[datetime]:
        now = datetime.now()
        all_takings = self.takings[drug_index]
        next_taking = None

        for taking_time in all_takings:
            if taking_time > now:
                next_taking = taking_time
                break

        return next_taking


# Пример использования
drug1 = Drug(drug="Аспирин", periodicity=2, duration_days=3)  # Каждые 2 часа, 3 дня
drug2 = Drug(drug="Парацетамол", periodicity=1, duration_days=5)  # Каждый час, 5 дней

user = User(
    user_id=123,
    first_time=datetime(2025, 3, 9, 12, 55),
    drugs=[drug1, drug2]
)

user.generate_scheduled_times()

print(f"ID пользователя: {user.user_id}")
print(f"Первое время приёма: {user.first_time}")

for i, drug in enumerate(user.drugs):
    print(f"\nЛекарство {i + 1}: {drug.drug}")
    print(f"  График приема: {user.takings[i]}")
    print(f"  Последний день приема: {user.last_day_times[i]}")

    next_taking = user.get_next_taking(i)
    if next_taking:
        print(f"  Ближайшее время приема: {next_taking}")
    else:
        print("  Нет ближайшего времени приема в будущем.")