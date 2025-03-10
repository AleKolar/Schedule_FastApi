from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.DB.database import get_db, create_tables, delete_tables
from src.DB.repository.repository import UserRepository
from src.models import SchemaUser, User

@asynccontextmanager
async def lifespan(app: FastAPI):
   await create_tables()
   print("База готова")
   yield
   await delete_tables()
   print("База очищена")

app = FastAPI(lifespan=lifespan)

@app.post("/", response_model=SchemaUser)
async def create_author(data: User, db: AsyncSession = Depends(get_db)):
    return await UserRepository.create_schedule(data, db)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
