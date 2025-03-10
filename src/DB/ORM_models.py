from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship, DeclarativeBase
from datetime import datetime

class Model(DeclarativeBase):
   pass

class DrugOrm(Model):
    __tablename__ = 'drugs'

    id = Column(Integer, primary_key=True, index=True)
    drug = Column(String, nullable=False)  # Наименование лекарства
    periodicity = Column(Integer, nullable=False)  # Периодичность приёмов в часах
    duration_days = Column(Integer, nullable=True)  # Продолжительность лечения в днях (Optional)
    user_id = Column(Integer, ForeignKey('users.id'))

    user = relationship("User", back_populates="drugs", lazy='joined')

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

class UserOrm(Model):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, unique=True)  # Идентификатор пациента (user_id)
    first_time = Column(DateTime, nullable=False)  # Дата и время первого приема (YYYY-MM-DD HH:MM)

    drugs = relationship("Drug", back_populates="user", cascade="all, delete-orphan", lazy='joined')
    takings = Column(String, default='[]')  # Здесь можно хранить JSON с расписанием
    last_day_times = Column(String, default='[]')  # Здесь можно хранить JSON с последними днями

    def __init__(self, user_id: int, first_time: datetime):
        self.user_id = user_id
        self.first_time = first_time

    def model_dump(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "first_time": self.first_time.strftime("%Y-%m-%d %H:%M:%S") if self.first_time else None,
            "drugs": [drug.model_dump() for drug in self.drugs],
            "takings": self.takings,
            "last_day_times": self.last_day_times
        }