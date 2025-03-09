from datetime import datetime, timedelta  
from typing import List, Optional  

from pydantic import BaseModel, Field, model_validator  


class Drug(BaseModel):  
    """  
    Модель для лекарства и его параметров приема.
    """  
    drug: str = Field(..., description="Наименование лекарства")  
    periodicity: int = Field(..., description="Периодичность приёмов в часах")  
    duration_days: Optional[int] = Field(None, description="Продолжительность лечения в днях (Optional)")  

class User(BaseModel):  
    """  
    Модель для пользователя и его расписания приема лекарств.
    """  
    user_id: int = Field(..., description="Идентификатор пациента (user_id)")  
    first_time: datetime = Field(..., description="Дата и время первого приема (YYYY-MM-DD HH:MM)")  
    drugs: List[Drug] = Field(..., description="Список назначенных лекарств")  
    takings: List[List[datetime]] = []  # Список списков времен приема для каждого лекарства, такое было в моем Django проекте, подход имеется в виду
    last_day_times: List[Optional[datetime]] = []  # Список последних дней приема для каждого лекарства  

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

    # Здесь я начал путаться и воспользовался помощью "индийского программиста", но логика от и до моя!
    @model_validator(mode='after')  
    def generate_scheduled_times(self):  
        """Генерируем расписание приемов для каждого лекарства."""  
        self.takings = []  # Инициализируем список takings  
        self.last_day_times = [] # Инициализируем список last_day_times  

        for drug in self.drugs:  
            first_time_rounded = self.round_minute(self.first_time)  
            takings = []  

            # Вычисляем время окончания приема в последний день
            end_time_last_day = first_time_rounded - timedelta(hours=drug.periodicity)
            # Рассчитываем время приемов на каждый день лечения
            for day in range(drug.duration_days):
                current_date = first_time_rounded.date() + timedelta(days=day)  # Получаем дату текущего дня

                # Устанавливаем начальное время для текущего дня
                schedule_time = datetime.combine(current_date, datetime.min.time()).replace(hour=8)

                # Определяем конечное время для текущего дня
                if day == drug.duration_days - 1: # Если это последний день
                    end_time_day = end_time_last_day.replace(year=current_date.year, month=current_date.month, day=current_date.day) # Устанавливаем дату последнего дня
                else:
                    end_time_day = datetime.combine(current_date, datetime.min.time()).replace(hour=22) # Иначе до 22:00

                # Пока текущее время меньше конечного времени дня, добавляем время приема
                while schedule_time < end_time_day:
                    if schedule_time >= first_time_rounded and schedule_time.date() == current_date:
                         takings.append(schedule_time)
                    schedule_time += timedelta(hours=drug.periodicity)

            self.takings.append(takings)

            if takings:
                self.last_day_times.append(takings[-1])
            else:
                self.last_day_times.append(None)
        return self


    def get_next_taking(self, drug_index: int) -> Optional[datetime]:
        """
        Вычисляет ближайшее время приема для конкретного лекарства.
        """
        now = datetime.now()
        takings = self.takings[drug_index]
        next_taking = None

        # Находим ближайшее время приема из списка takings
        for taking_time in takings:
            if taking_time > now:
                next_taking = taking_time
                break  # Нашли ближайшее, выходим из цикла

        return next_taking


# Пример использования
drug1 = Drug(drug="Аспирин", periodicity=1, duration_days=3)
drug2 = Drug(drug="Парацетамол", periodicity=4, duration_days=5)

user = User(
    user_id=123,
    first_time=datetime(2025, 3, 9, 13, 00),
    drugs=[drug1, drug2]
)


user.generate_scheduled_times()

print(f"ID пользователя: {user.user_id}")  
print(f"Первое время приёма: {user.first_time}")  

for i, drug in enumerate(user.drugs):  
    print(f"\nЛекарство {i+1}: {drug.drug}")  
    print(f"  График приема: {user.takings[i]}")  
    print(f"  Последний день приема: {user.last_day_times[i]}")  

    next_taking = user.get_next_taking(i)  
    if next_taking:  
        print(f"  Ближайшее время приема: {next_taking}")  
    else:  
        print("  Нет ближайшего времени приема в будущем.")  