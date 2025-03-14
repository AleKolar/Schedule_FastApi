from datetime import datetime, timedelta
from typing import Tuple, List, Optional

from src.models import Drug


class ScheduleGenerator:
    @staticmethod
    def round_minute(value: datetime) -> datetime:
        minute = value.minute
        if 1 <= minute <= 15:
            return value.replace(minute=15, second=0, microsecond=0)
        elif 16 <= minute <= 30:
            return value.replace(minute=30, second=0, microsecond=0)
        elif 31 <= minute <= 45:
            return value.replace(minute=45, second=0, microsecond=0)
        else:
            return value.replace(hour=(value.hour + 1) % 24, minute=0, second=0, microsecond=0)

    @staticmethod
    def generate_scheduled_times(drugs: List[Drug], first_time: datetime) -> Tuple[List[List[datetime]], List[Optional[datetime]]]:
        schedule = []
        last_day_times = []

        for drug in drugs:
            first_time_rounded = ScheduleGenerator.round_minute(first_time)
            drug_takings = []

            for day in range(drug.duration_days or 0):
                current_date = first_time_rounded.date() + timedelta(days=day)

                if day == 0:
                    schedule_time = first_time_rounded
                else:
                    schedule_time = datetime.combine(current_date, datetime.min.time()).replace(hour=8)

                end_time_day = datetime.combine(current_date, datetime.min.time()).replace(hour=22)

                while schedule_time < end_time_day:
                    if schedule_time.hour >= 8:
                        drug_takings.append(schedule_time)
                    schedule_time += timedelta(hours=drug.periodicity)

            schedule.append(drug_takings)

            if drug_takings:
                last_drug_time = first_time_rounded + timedelta(days=drug.duration_days) - timedelta(hours=drug.periodicity)
                last_day_times.append(last_drug_time)
            else:
                last_day_times.append(None)

        return schedule, last_day_times

