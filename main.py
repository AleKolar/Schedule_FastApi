import uuid
from contextlib import asynccontextmanager

from sqlalchemy.orm import Session

from src.models import ScheduleCreate
from src.repository.repository import create_schedule, get_user_schedules, get_schedule_by_id, get_next_schedule



import uvicorn
from fastapi import FastAPI
from fastapi.params import Depends

from src.DB.database import get_db, create_tables, delete_tables



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
def create_schedule_route(schedule: ScheduleCreate, db: Session = Depends(get_db)):
    schedule_id = create_schedule(
        first_time=schedule.first_time,
        drug=schedule.drug,
        periodicity=schedule.periodicity,
        duration_days=schedule.duration_days,
        user_id=schedule.user_id,
        db=db
    )
    return {"schedule_id": schedule_id}

# Обработчик для получения всех расписаний пользователя
@app.get("/schedules")
def get_schedules_route(user_id: uuid.UUID, db: Session = Depends(get_db)):
    schedule_ids = get_user_schedules(user_id, db)
    return {"schedule_ids": schedule_ids}

# Обработчик для получения конкретного расписания
@app.get("/schedule")
def get_schedule_route(user_id: uuid.UUID, schedule_id: int, db: Session = Depends(get_db)):
    schedule_data = get_schedule_by_id(user_id, schedule_id, db)
    return schedule_data

# Обработчик для получения следующего времени приема
@app.get("/next_takings")
def get_next_takings_route(user_id: uuid.UUID, db: Session = Depends(get_db)):
    next_takings = get_next_schedule(user_id, db)
    return {"next_takings": next_takings}

@app.get("/")
async def read_root():
    return {"Hello": "World"}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
