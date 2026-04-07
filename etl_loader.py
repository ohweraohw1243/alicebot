import os
from datetime import datetime, timedelta
import clickhouse_connect
from dotenv import load_dotenv

from moyklass import fetch_moyklass_schedule
from nstu import fetch_nstu_schedule

load_dotenv()

# Соответствие дней недели НГТУ номерам дней
WEEKDAYS = {
    "Понедельник": 0,
    "Вторник": 1,
    "Среда": 2,
    "Четверг": 3,
    "Пятница": 4,
    "Суббота": 5,
    "Воскресенье": 6
}

def get_client():
    return clickhouse_connect.get_client(
        host=os.getenv("CH_HOST", "localhost"),
        port=int(os.getenv("CH_PORT", 8123)),
        username=os.getenv("CH_USER", "default"),
        password=os.getenv("CH_PASSWORD", "")
    )

def insert_events(events: list):
    """
    Вставляет список распарсенных событий в БД clickhouse.
    Ожидаемый формат строки:
    [id, event_date, event_time, title, event_type, duration_min, notes]
    """
    if not events:
        print("Нет данных для вставки.")
        return
        
    client = get_client()
    columns = ['id', 'event_date', 'event_time', 'title', 'event_type', 'duration_min', 'notes']
    
    try:
        client.insert('schedule.events', events, column_names=columns)
        print(f"Успешно загружено {len(events)} событий в базу данных.")
    except Exception as e:
        print(f"Ошибка при загрузке данных: {e}")

def run_etl():
    print("Начат процесс ETL для сбора расписания...")
    db_events = []
    
    # 1. Извлекаем (Extract) и трансформируем (Transform) НГТУ (без авторизации)
    print("Собираем расписание из НГТУ...")
    try:
        nstu_raw = fetch_nstu_schedule("АВТ-11")
        # Вычисляем даты для текущей недели
        today = datetime.today()
        start_of_week = today - timedelta(days=today.weekday())
        
        for item in nstu_raw:
            day_idx = WEEKDAYS.get(item["day"])
            if day_idx is not None:
                # Определяем дату на текущей неделе
                event_date = (start_of_week + timedelta(days=day_idx)).date()
                
                # Время в НГТУ обычно в формате "08:30 - 10:00" - вытаскиваем начало
                begin_time = item["time"].split("-")[0].strip() if "-" in item["time"] else item["time"]
                
                # Добавляем в общий список
                # id, event_date, event_time, title, event_type, duration_min, notes
                db_events.append([
                    f"nstu_{event_date}_{begin_time}",
                    event_date,
                    begin_time,
                    item["subject"],
                    "university",
                    90,
                    f"Аудитория: {item['room']} | Неделя: {item['week_type']}"
                ])
    except Exception as e:
        print(f"Ошибка парсинга НГТУ: {e}")
        
    # 2. Извлекаем (Extract) и трансформируем (Transform) МойКласс (если есть токены)
    print("Собираем расписание из МойКласс (CRM)...")
    # Добавьте сюда ваши реальные данные для авторизации (лучше вынести их в .env)
    # mk_events = fetch_moyklass_schedule(...)
    # for ev in mk_events: db_events.append([ev["id"], ev["date"], ev["begin_time"], ev["title"], "tutoring", 60, ""])
    print("Пропуск МойКласс (отсутствуют credentials в скрипте)")

    # 3. Загружаем (Load) в ClickHouse
    print("Загрузка данных в ClickHouse...")
    insert_events(db_events)

if __name__ == "__main__":
    run_etl()
