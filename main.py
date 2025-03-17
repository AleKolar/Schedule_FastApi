import logging
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession

from src.DB.ORM_models import UserOrm, ScheduleCreateORM
from src.models import SchemaScheduleCreate
from fastapi import FastAPI, HTTPException, Depends

from src.DB.database import get_db, create_tables, delete_tables, new_session
from src.repository.repository import TaskRepository
from src.repository.utils import ScheduleGeneratorTimes, serialize_datetime


@asynccontextmanager
async def lifespan(app: FastAPI):
   await create_tables()
   print("База готова")
   yield
   await delete_tables()
   print("База очищена")

app = FastAPI(lifespan=lifespan)

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.post("/schedule")
async def create_schedule(schedule_create: SchemaScheduleCreate, db: AsyncSession = Depends(get_db)):
    logger.info("Received request to create schedule for user_id: %s", schedule_create.user_id)

    try:
        # Генерация расписания для всех лекарств
        schedule, last_day_times = ScheduleGeneratorTimes.generate_scheduled_times(schedule_create)
        logger.info("Generated schedule: %s", schedule)

        # Используем TaskRepository для получения пользователя
        user = await TaskRepository.get_user(schedule_create.user_id)
        logger.info("Fetched user: %s", user)

        # Проверка, найден ли пользователь
        if user is None:
            logger.warning("User not found for user_id: %s. Creating a new user.", schedule_create.user_id)
            user = UserOrm(user_id=schedule_create.user_id)  # создаем нового пользователя
            user.schedule = []  # Инициализируем расписание
            user.last_day_times = []  # Инициализируем последние дни, если это необходимо

        # Сериализуем расписание и последние дни
        user.schedule.append(serialize_datetime(schedule))
        user.last_day_times.extend(serialize_datetime(last_day_times))
        logger.info("Updated user schedule and last day times.")

        # Сохраните пользователя в базе данных
        db.add(user)
        await db.commit()
        logger.info("Schedule saved successfully for user_id: %s", schedule_create.user_id)

        return {"message": "Schedule created successfully", "schedule": schedule, "last_day_times": last_day_times}

    except Exception as e:
        logger.exception("An error occurred while creating schedule for user_id: %s", schedule_create.user_id)
        raise HTTPException(status_code=500, detail="Internal Server Error")


# @app.get("/schedules")
# def get_user_schedules(user_id: uuid.UUID, db: Session = Depends(get_db)):
#     schedules = get_user_schedules(user_id, db)
#     return {"schedules": schedules}
#
#
# @app.get("/schedule")
# def get_schedule(user_id: uuid.UUID, schedule_id: int, db: Session = Depends(get_db)):
#     stmt = select(UserOrm).filter(UserOrm.user_id == user_id)
#     user = db.execute(stmt).scalars().first()
#
#     if not user:
#         raise HTTPException(status_code=404, detail="Пользователь не найден")
#
#     schedule = next((drug for drug in user.drugs if drug.id == schedule_id), None)
#     if not schedule:
#         raise HTTPException(status_code=404, detail="Расписание не найдено")
#
#         # Генерация расписания для данного лекарства
#     scheduled_times, _ = ScheduleGeneratorTimes.generate_scheduled_times(
#         schedule, user.first_time
#     )
#
#     return {
#         "schedule": {
#             "schedule_id": schedule.id,
#             "drug": schedule.drug,
#             "scheduled_times": scheduled_times
#         }
#     }
#
# @app.get("/next_takings")
# def get_next_takings(user_id: uuid.UUID, db: Session = Depends(get_db)):
#     return get_next_schedule(user_id, db)

@app.get("/")
async def read_root():
    return {"Hello": "World"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001, log_level="info")
