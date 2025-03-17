from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import List, Tuple, Optional, Any, Dict, Union

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.models import SchemaScheduleCreate


class ScheduleGeneratorTimes:
    TIME_FORMAT = '%Y-%m-%d %H:%M'
    DAY_START_HOUR = 8
    DAY_END_HOUR = 22

    @staticmethod
    def round_minute(value: Optional[datetime]) -> Optional[datetime]:
        """ Округляет минуты во времени до ближайших 15, 30, 45 или 00 """
        if value is None:
            return None

        minute = value.minute
        if 1 <= minute <= 15:
            rounded_time = value.replace(minute=15, second=0, microsecond=0)
        elif 16 <= minute <= 30:
            rounded_time = value.replace(minute=30, second=0, microsecond=0)
        elif 31 <= minute <= 45:
            rounded_time = value.replace(minute=45, second=0, microsecond=0)
        else:
            rounded_time = value.replace(hour=(value.hour + 1) % 24, minute=0, second=0, microsecond=0)

        return rounded_time

    @classmethod
    def generate_scheduled_times(cls, schema: SchemaScheduleCreate) -> Tuple[
        List[List[Dict[str, Union[str, datetime]]]], List[Optional[datetime]]]:

        schedule = []
        last_day_times = []
        first_time_rounded = cls.round_minute(schema.first_time)

        if first_time_rounded is None:
            return [], []

            # Приводим к timezone-aware datetime
        first_time_dt = first_time_rounded.replace(tzinfo=timezone.utc)

        # Проходим по каждому лекарству в списке drugs
        for drug in schema.drugs:
            if drug.duration_days is None or drug.duration_days <= 0:
                print(f"Ошибка: Некорректная продолжительность лечения для лекарства {drug.drug}")
                duration = 22250  # Установите значение по умолчанию, если необходимо
            else:
                duration = drug.duration_days

            if drug.periodicity <= 0:
                print(f"Ошибка: Некорректная периодичность приема лекарства {drug.drug}")
                continue

            drug_schedule = []

            # Генерируем расписание для текущего лекарства
            for day in range(duration):
                current_date = first_time_dt.date() + timedelta(days=day)
                schedule_time = datetime.combine(current_date, datetime.min.time()).replace(
                    hour=ScheduleGeneratorTimes.DAY_START_HOUR, tzinfo=timezone.utc)
                end_time_day = datetime.combine(current_date, datetime.min.time()).replace(
                    hour=ScheduleGeneratorTimes.DAY_END_HOUR, tzinfo=timezone.utc)

                while schedule_time < end_time_day:
                    if ScheduleGeneratorTimes.DAY_START_HOUR <= schedule_time.hour < ScheduleGeneratorTimes.DAY_END_HOUR:
                        # Добавляем словарь с временем и названием лекарства
                        drug_schedule.append({"time": schedule_time, "drug_name": drug.drug})
                    schedule_time += timedelta(hours=drug.periodicity)

            schedule.append(drug_schedule)

            if drug_schedule:
                last_day_times.append(drug_schedule[-1]["time"])  # последний элемент - это datetime
            else:
                last_day_times.append(None)

        return schedule, last_day_times