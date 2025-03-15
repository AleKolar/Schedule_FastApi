import uuid

from src.DB.ORM_models import UserOrm, ScheduleCreateORM
from src.DB.database import new_session
from src.models import SchemaScheduleCreate, ScheduleCreate


class TaskRepository:
    @classmethod
    async def get_user(cls, user_id: uuid.UUID):
        async with new_session() as session:
            user = await session.get(UserOrm, user_id)
            return user

    @classmethod
    async def add_task(cls, schedule: SchemaScheduleCreate):
        async with new_session() as session:
            # Получаем данные из schedule
            data = schedule.model_dump()
            new_schedule = ScheduleCreateORM(**data)
            session.add(new_schedule)
            await session.flush()
            await session.commit()
            return new_schedule