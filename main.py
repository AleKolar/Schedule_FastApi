from contextlib import asynccontextmanager
from src.models import SchemaScheduleCreate
from fastapi import FastAPI, HTTPException

from src.DB.database import get_db, create_tables, delete_tables
from src.repository.repository import TaskRepository
from src.repository.utils import ScheduleGeneratorTimes


@asynccontextmanager
async def lifespan(app: FastAPI):
   await create_tables()
   print("База готова")
   yield
   await delete_tables()
   print("База очищена")

app = FastAPI(lifespan=lifespan)

# Обработчик для создания расписания
@app.post("/schedule")
async def create_schedule(schedule: SchemaScheduleCreate):
    try:
        # Получаем пользователя
        user = await TaskRepository.get_user(schedule.user_id)

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

            # Генерируем расписание и последний день приема
        generated_schedule, last_day_times = ScheduleGeneratorTimes.generate_scheduled_times(user)

        # Сохраняем в базе данных
        new_schedule = await TaskRepository.add_task(schedule)

        # Возвращаем расписание и последний день приема
        return {
            "user_id": user.user_id,  # Возвращаем идентификатор пользователя
            "schedule": generated_schedule,
            "last_day_times": last_day_times,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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
