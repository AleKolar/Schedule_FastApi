import uuid
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, UUID
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from datetime import datetime  # Исправляем импорт

from src.models import ScheduleRequest


class Model(DeclarativeBase):
    pass

class UserOrm(Model):
    __tablename__ = 'users'
    ''' Таблица для пациентов с их расписанием приема лекарств '''

    user_id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    first_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_day_times: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    schedule: Mapped[datetime] = mapped_column(String, default='[]')

    drugs = relationship("DrugOrm", back_populates="user", cascade="all, delete-orphan", lazy='joined')
    schedules = relationship("ScheduleRequest", back_populates="user", cascade="all, delete-orphan")

    def model_dump(self):
        return {
            "user_id": self.user_id,
            "drugs": [drug.model_dump() for drug in self.drugs],
            "first_time": self.first_time,
            "schedule": self.schedule,  # Исправляем опечатку
            "last_day_times": self.last_day_times
        }

class DrugOrm(Model):
    __tablename__ = 'drugs'
    ''' Таблица лекарств: название, периодичность приёма, курс в днях '''

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    drug: Mapped[str] = mapped_column(String, nullable=False)
    periodicity: Mapped[int] = mapped_column(Integer, nullable=False)
    duration_days: Mapped[int] = mapped_column(Integer, nullable=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey('users.user_id'))

    user = relationship("UserOrm", back_populates="drugs", lazy='joined')

    @property
    def is_continuous(self) -> bool:
        """Проверяет, является ли прием лекарства непрерывным."""
        effective_duration_days = self.duration_days if self.duration_days is not None else 25550
        return effective_duration_days > 0

    def model_dump(self):
        return {
            "id": self.id,
            "drug": self.drug,
            "periodicity": self.periodicity,
            "duration_days": self.duration_days,
            "user_id": self.user_id,
            "is_continuous": self.is_continuous
        }
class ScheduleRequestORM(ScheduleRequest):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True,
                                    description="Идентификатор расписания")
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.user_id"),
                                               description="Идентификатор пользователя, которому принадлежит расписание")
    first_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    drug: Mapped[str] = mapped_column(String, nullable=False)
    periodicity: Mapped[int] = mapped_column(Integer, nullable=False)
    duration_days: Mapped[int] = mapped_column(Integer, nullable=True)

    user = relationship("UserOrm", back_populates="schedules")