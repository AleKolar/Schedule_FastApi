import uuid
from typing import Optional, List, Type

from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from datetime import datetime

from src.DB.ORM_models import ScheduleRequestORM
from src.repository.utils import ScheduleGenerator  # Импортируем класс ScheduleGenerator для расчета расписаний


def create_schedule(
        first_time: datetime,
        drug: str,
        periodicity: int,
        duration_days: Optional[int],
        user_id: uuid.UUID,
        db: Session
) -> int:
    # Создаем новый объект расписания
    new_schedule = ScheduleRequestORM(
        first_time=first_time,
        drug=drug,
        periodicity=periodicity,
        duration_days=duration_days,
        user_id=user_id
    )

    try:
        db.add(new_schedule)
        db.commit()
        db.refresh(new_schedule)
        return new_schedule.id
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Ошибка при создании расписания")


def get_user_schedules(user_id: uuid.UUID, db: Session) -> List[int]:
    stmt = select(ScheduleRequestORM).filter(ScheduleRequestORM.user_id == user_id)
    schedules = db.execute(stmt).scalars().all()
    return [schedule.id for schedule in schedules]


def get_schedule_by_id(user_id: uuid.UUID, schedule_id: int, db: Session) -> Type[ScheduleRequestORM]:
    stmt = select(ScheduleRequestORM).filter(
        ScheduleRequestORM.user_id == user_id,
        ScheduleRequestORM.id == schedule_id
    )
    schedule = db.execute(stmt).scalars().first()

    if not schedule:
        raise HTTPException(status_code=404, detail="Расписание не найдено")

        # Генерация расписания
    scheduled_times, last_day_times = ScheduleGenerator.generate_scheduled_times(
        [schedule], schedule.first_time
    )

    return ScheduleRequestORM


def get_next_schedule(user_id: uuid.UUID, db: Session) -> List[dict]:
    stmt = select(ScheduleRequestORM).filter(ScheduleRequestORM.user_id == user_id)
    schedules = db.execute(stmt).scalars().all()

    next_schedule = []

    for schedule in schedules:
        scheduled_times, _ = ScheduleGenerator.generate_scheduled_times(
            [schedule], schedule.first_time
        )

        # Вычисляем время для следующего приема
        now = datetime.utcnow()
        for times in scheduled_times:
            next_time = next((time for time in times if time > now), None)
            if next_time:
                next_schedule.append({
                    "schedule_id": schedule.id,
                    "next_taking": next_time
                })

    return next_schedule