import enum  
from datetime import datetime, timedelta  
from typing import List, Optional  

from pydantic import BaseModel, Field, model_validator  


class Periodicity(enum.Enum):  
    ONCE_A_DAY = "ежедневно"  
    HOURLY = "ежечасно"  


# Определяем класс для входящих данных  
class ScheduleCreateRequest(BaseModel):  
    drug: str = Field(..., description="Наименование лекарства")  
    periodicity: Periodicity = Field(..., description="Периодичность приёмов")  
    duration_days: Optional[int] = Field(None, description="Продолжительность лечения в днях (Optional)")  
    user_id: int = Field(..., description="Идентификатор пациента (user_id)")  
    first_time: datetime = Field(..., description="Дата и время первого приема (YYYY-MM-DD HH:MM)")  


# Определяем класс ответа  
class ScheduleDetailsResponse(BaseModel):  
    schedule_id: int  
    drug: str  
    periodicity: Periodicity  
    duration_days: Optional[int]  
    user_id: int  
    first_time: datetime  
    takings: List[datetime] = []  # Список времени приемов (пустой по умолчанию)  
    last_day_time: Optional[datetime] = None  # Последний день приема (расчетный)  

    @classmethod  
    def round_minute(cls, value: datetime):  
        """Округляем минуты до ближайшего временного диапазона."""  
        minute = value.minute  
        if 1 <= minute <= 15:  
            return value.replace(minute=15, second=0, microsecond=0)  
        elif 16 <= minute <= 30:  
            return value.replace(minute=30, second=0, microsecond=0)  
        elif 31 <= minute <= 45:  
            return value.replace(minute=45, second=0, microsecond=0)  
        else:  
            return value.replace(hour=(value.hour + 1) % 24, minute=0, second=0, microsecond=0)  

    @model_validator(mode='after')  
    def generate_scheduled_times(self):  
        """Генерируем расписание приемов."""  
        first_time_rounded = self.round_minute(self.first_time)  
        takings = []  

        for day in range(self.duration_days):  
            current_date = first_time_rounded + timedelta(days=day)  

            if self.periodicity == Periodicity.HOURLY:  
                hourly_time = current_date  # Начинаем с округленного времени  
                end_time_for_day = current_date.replace(hour=first_time_rounded.hour, minute=first_time_rounded.minute, second=0, microsecond=0) + timedelta(days=1) - timedelta(hours=1)  

                if day == self.duration_days - 1:  # Если это последний день  
                    end_time_for_day = first_time_rounded + timedelta(days=day)  


                while hourly_time <= end_time_for_day:  
                    takings.append(hourly_time)  
                    hourly_time += timedelta(hours=1)  

            elif self.periodicity == Periodicity.ONCE_A_DAY:  
                takings.append(current_date)  

        if takings:  
            self.last_day_time = takings[-1]  
            self.takings = sorted(takings)  

        return self  

class NextTakingsResponse(BaseModel):  
    """  
    Модель ответа для ближайших приемов лекарств.  
    """  
    drug: str  
    taking_time: datetime  

    @classmethod  
    def get_next_taking(cls, takings: List[datetime]):  
        """  
        Выбирает ближайшее время приема из списка takings, но не позднее, чем через час.  
        """  
        now = datetime.now()  
        next_taking = None  
        time_difference_limit = timedelta(hours=1)  

        for taking_time in takings:  
            time_difference = taking_time - now  
            if time_difference > timedelta(0) and time_difference <= time_difference_limit:  
                if next_taking is None or taking_time < next_taking:  
                    next_taking = taking_time  

        if next_taking is None:  
            return None  

        return next_taking  


# Пример использования  
schedule_details = ScheduleDetailsResponse(  
    schedule_id=1,  
    drug="Аспирин",  
    periodicity=Periodicity.HOURLY,  
    duration_days=3,  
    user_id=123,  
    first_time=datetime(2025, 3, 9, 11, 11),  # Пример времени  
)  
# Теперь takings должен содержать результаты из валидатора  
print(f"График приема лекарства: {schedule_details.takings}")  
print(f"Последний день приема лекарства: {schedule_details.last_day_time}")  
print(f"Первое время: {schedule_details.first_time}")  
print(f"Периодичность: {schedule_details.periodicity}")  
print(f"Продолжительность (дней): {schedule_details.duration_days}")  
print(f"Последний день приема: {schedule_details.last_day_time}")  