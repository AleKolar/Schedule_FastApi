from sqlalchemy.ext.asyncio import AsyncSession
from src.DB.ORM_models import UserOrm
from src.models import User
import datetime
from typing import List

class UserRepository:

    @classmethod
    async def round_minute(cls, value: datetime) -> datetime:
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
    async def create_schedule(cls, data: User, db: AsyncSession) -> UserOrm:
        model = UserOrm(**data.dict())
        db.add(model)
        await db.flush()
        await db.commit()
        return model

    @classmethod
    def generate_scheduled_times(cls, user: User) -> (List[str], List[str]):
        takings = []
        last_day_times = []
        first_time_rounded = cls.round_minute(user.first_time)

        for drug in user.drugs:
            drug_takings = []

            # !!! Устанавливаем количество дней, в течение которых лекарство принимается !!!
            duration = drug.duration_days if drug.duration_days is not None else 300  # Например, постоянный прием на 300 дней для простоты

            for day in range(duration):
                current_date = first_time_rounded.date() + datetime.timedelta(days=day)
                schedule_time = datetime.datetime.combine(current_date, datetime.datetime.min.time()).replace(hour=8)

                end_time_day = datetime.datetime.combine(current_date, datetime.datetime.min.time()).replace(hour=22)

                while schedule_time < end_time_day:
                    if schedule_time.hour >= 8:
                        drug_takings.append(schedule_time.isoformat())
                    schedule_time += datetime.timedelta(hours=drug.periodicity)

            takings.append(drug_takings)

            if drug_takings:
                last_drug_time = first_time_rounded + datetime.timedelta(days=drug.duration_days) - datetime.timedelta(hours=drug.periodicity)
                last_day_times.append(last_drug_time.isoformat())
            else:
                last_day_times.append(None)

        return takings, last_day_times