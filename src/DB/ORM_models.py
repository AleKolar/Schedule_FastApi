import uuid
from typing import List, Optional, Union, Dict

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, UUID, JSON
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column, declarative_base
from datetime import datetime, timezone


DeclarativeBase = declarative_base()

class Model(DeclarativeBase):
    __abstract__ = True  # Абстрактный базовый класс
    pass

class UserOrm(Model):
    __tablename__ = 'users'

    user_id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    drugs: Mapped[List["DrugOrm"]] = relationship("DrugOrm", back_populates="user", lazy='joined')
    schedule: Mapped[List[List[Dict[str, Union[str, datetime]]]]] = mapped_column(JSON, default=[])
    last_day_times: Mapped[List[Optional[datetime]]] = mapped_column(JSON, default=[])

    def model_dump(self):
        return {
            "user_id": self.user_id,
            "schedule": self.schedule,
            "last_day_times": self.last_day_times,
        }

class DrugOrm(Model):
    __tablename__ = 'drugs'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    drug: Mapped[str] = mapped_column(String, nullable=False)
    periodicity: Mapped[int] = mapped_column(Integer, nullable=False)
    duration_days: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey('users.user_id'))

    # Изменение: user теперь будет ссылкой на UserOrm
    user: Mapped["UserOrm"] = relationship("UserOrm", back_populates="drugs", lazy='joined')

    @property
    def is_continuous(self) -> bool:
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


class ScheduleCreateORM(Model):
    __tablename__ = 'schedule'

    schedule_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    first_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now(timezone.utc))
    drug: Mapped[str] = mapped_column(String, nullable=False)
    periodicity: Mapped[int] = mapped_column(Integer, nullable=False)
    duration_days: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('users.user_id'))

    def model_dump(self):
        return {
            "id": self.id,
            "first_time": self.first_time,
            "drug": self.drug,
            "periodicity": self.periodicity,
            "duration_days": self.duration_days,
            "user_id": self.user_id,
        }