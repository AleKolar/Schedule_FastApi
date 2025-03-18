from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from typing import List, Tuple, Optional, Any, Dict, Union

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from src.models import SchemaScheduleCreate


class ScheduleGeneratorTimes:
    DAY_START_HOUR = 8
    DAY_END_HOUR = 22

    @staticmethod
    def round_minute(value: datetime) -> datetime:
        """Округляет минуты во времени до ближайших 15, 30, 45 или 00"""
        if value is None:
            return None

        minute = value.minute
        if 1 <= minute <= 15:
            return value.replace(minute=15, second=0, microsecond=0)
        elif 16 <= minute <= 30:
            return value.replace(minute=30, second=0, microsecond=0)
        elif 31 <= minute <= 45:
            return value.replace(minute=45, second=0, microsecond=0)
        else:
            return value.replace(hour=(value.hour + 1) % 24, minute=0, second=0, microsecond=0)

    @classmethod
    def generate_scheduled_times(cls, schedule_schema) -> Tuple[
        List[Dict[str, Union[datetime, str]]], List[Union[datetime, None]]]:
        schedule = []
        last_day_times = []
        first_time_rounded = cls.round_minute(schedule_schema.first_time)

        if first_time_rounded is None:
            return [], []  # Возвращаем пустые списки, если время некорректно

        # Приводим к timezone-aware datetime
        first_time_dt = first_time_rounded.replace(tzinfo=timezone.utc)

        if schedule_schema.duration_days is None or schedule_schema.duration_days <= 0:
            print(f"Ошибка: Некорректная продолжительность лечения для лекарства {schedule_schema.drug}")
            return [], []

        duration = schedule_schema.duration_days

        for day in range(duration):
            current_date = first_time_dt.date() + timedelta(days=day)
            schedule_time = None

            if day == 0:
                schedule_time = first_time_dt
            elif day == duration - 1:  # Если это последний день
                schedule_time = datetime.combine(current_date, datetime.min.time()).replace(
                    hour=ScheduleGeneratorTimes.DAY_START_HOUR, minute=15, tzinfo=timezone.utc)  # Начинаем с 08:15
            else:
                schedule_time = datetime.combine(current_date, datetime.min.time()).replace(
                    hour=ScheduleGeneratorTimes.DAY_START_HOUR, minute=15, tzinfo=timezone.utc)  # Начинаем с 08:15

            end_time_day = datetime.combine(current_date, datetime.min.time()).replace(
                hour=ScheduleGeneratorTimes.DAY_END_HOUR, minute=0, tzinfo=timezone.utc)

            last_time_for_day = None  # Для отслеживания последнего приема в день

            # На первом дне
            if day == 0:
                while schedule_time < end_time_day:
                    if ScheduleGeneratorTimes.DAY_START_HOUR <= schedule_time.hour < ScheduleGeneratorTimes.DAY_END_HOUR:
                        schedule.append({
                            "time": schedule_time,
                            "drug_name": schedule_schema.drug,
                            "user_id": schedule_schema.user_id
                        })
                        last_time_for_day = schedule_time

                    schedule_time += timedelta(hours=schedule_schema.periodicity)

            # На промежуточных днях
            elif 0 < day < duration - 1:
                while schedule_time < end_time_day:
                    if ScheduleGeneratorTimes.DAY_START_HOUR <= schedule_time.hour < ScheduleGeneratorTimes.DAY_END_HOUR:
                        schedule.append({
                            "time": schedule_time,
                            "drug_name": schedule_schema.drug,
                            "user_id": schedule_schema.user_id
                        })
                        last_time_for_day = schedule_time

                    schedule_time += timedelta(hours=schedule_schema.periodicity)

            # На последнем дне
            elif day == duration - 1:
                while schedule_time < end_time_day:
                    if schedule_time.hour < 10:  # до 10:15 только
                        schedule.append({
                            "time": schedule_time,
                            "drug_name": schedule_schema.drug,
                            "user_id": schedule_schema.user_id
                        })
                        last_time_for_day = schedule_time

                    schedule_time += timedelta(hours=schedule_schema.periodicity)

            if last_time_for_day:
                last_day_times.append(last_time_for_day)  # Добавляем последнее время приема для дня

        return schedule, last_day_times




# Конвертация всех datetime-объектов в строку
def serialize_datetime(data):
    if isinstance(data, list):
        return [serialize_datetime(item) for item in data]
    elif isinstance(data, dict):
        return {key: serialize_datetime(value) for key, value in data.items()}
    elif isinstance(data, datetime):
        return data.isoformat()  # Конвертация datetime в строку в ISO формате
    elif isinstance(data, uuid.UUID):
        return str(data)  # Конвертация UUID в строку
    return data