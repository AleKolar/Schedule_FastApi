from sqlalchemy import inspect
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession
from src.DB.ORM_models import Model
from src.config.config import settings

DATABASE_URL = settings.get_db_url()
engine = create_async_engine(DATABASE_URL, future=True, echo=True)
new_session = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)

# Generator to get database sessions
async def get_db():
    async with new_session() as db:
        yield db

async def create_tables():
    async with engine.begin() as connection:
        await connection.run_sync(Model.metadata.create_all)

async def delete_tables():
    async with engine.begin() as connection:
        await connection.run_sync(Model.metadata.drop_all)