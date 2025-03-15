from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import List, Tuple, Optional, Any

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.models import User

class ScheduleGeneratorTimes:
    TIME_FORMAT = '%Y-%m-%d %H:%M'
    DAY_START_HOUR = 8
    DAY_END_HOUR = 22

    @staticmethod
    def round_minute(value: str) -> Optional[datetime]:
        """ Округляет минуты во времени до ближайших 15, 30, 45 или 00 """
        try:
            value_dt = datetime.strptime(value, ScheduleGeneratorTimes.TIME_FORMAT).replace(tzinfo=timezone.utc)
        except ValueError:
            print(f"Ошибка: Некорректный формат даты/времени: {value}")
            return None

        minute = value_dt.minute
        if 1 <= minute <= 15:
            rounded_time = value_dt.replace(minute=15, second=0, microsecond=0)
        elif 16 <= minute <= 30:
            rounded_time = value_dt.replace(minute=30, second=0, microsecond=0)
        elif 31 <= minute <= 45:
            rounded_time = value_dt.replace(minute=45, second=0, microsecond=0)
        else:
            rounded_time = value_dt.replace(hour=(value_dt.hour + 1) % 24, minute=0, second=0, microsecond=0)
        return rounded_time

    @classmethod
    def generate_scheduled_times(cls, user) -> Tuple[List[List[str]], List[Optional[datetime]]]:
        """ Генерирует расписание приема лекарств для пользователя """
        schedule = []
        last_day_times = []
        first_time_rounded = cls.round_minute(user.first_time)

        if first_time_rounded is None:
            return [], []

            # Приводим к timezone-aware datetime
        first_time_dt = first_time_rounded.replace(tzinfo=timezone.utc)

        for drug in user.drugs:
            if drug.duration_days is None or drug.duration_days <= 0:
                print(f"Ошибка: Некорректная продолжительность лечения")
                duration = 22250
            else:
                duration = drug.duration_days

            if drug.periodicity <= 0:
                print(f"Ошибка: Некорректная периодичность приема лекарства")
                continue

            drug_schedule = []

            for day in range(duration):
                current_date = first_time_dt.date() + timedelta(days=day)
                schedule_time = datetime.combine(current_date, datetime.min.time()).replace(
                    hour=ScheduleGeneratorTimes.DAY_START_HOUR, tzinfo=timezone.utc)
                end_time_day = datetime.combine(current_date, datetime.min.time()).replace(
                    hour=ScheduleGeneratorTimes.DAY_END_HOUR, tzinfo=timezone.utc)

                while schedule_time < end_time_day:
                    if ScheduleGeneratorTimes.DAY_START_HOUR <= schedule_time.hour < ScheduleGeneratorTimes.DAY_END_HOUR:
                        drug_schedule.append(schedule_time.strftime(ScheduleGeneratorTimes.TIME_FORMAT))
                    schedule_time += timedelta(hours=drug.periodicity)

            schedule.append(drug_schedule)

            if drug_schedule:
                last_drug_time = datetime.strptime(drug_schedule[-1], ScheduleGeneratorTimes.TIME_FORMAT).replace(
                    tzinfo=timezone.utc)
                last_day_times.append(last_drug_time)  ## datetime
            else:
                last_day_times.append(None)

        return schedule, last_day_times