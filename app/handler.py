import datetime
from app.db import get_events_for_date

def process_alice_request(req_data: dict) -> dict:
    """
    Распознает интент через keyword matching и формирует ответ.
    """
    request = req_data.get("request", {})
    command = request.get("command", "").lower()
    
    intent = "today" # Значение по умолчанию
    target_date = datetime.date.today()
    
    # Очень простой keyword matching
    if "завтра" in command:
        intent = "tomorrow"
        target_date += datetime.timedelta(days=1)
    elif "послезавтра" in command:
        intent = "day_after_tomorrow"
        target_date += datetime.timedelta(days=2)
    elif "сегодня" in command:
        intent = "today"
    else:
        # Проверяем дни недели
        weekdays = {
            "понедельник": 0,
            "вторник": 1,
            "сред": 2,
            "четверг": 3,
            "пятниц": 4,
            "суббот": 5,
            "воскресень": 6
        }
        for wd_word, wd_idx in weekdays.items():
            if wd_word in command:
                intent = f"weekday_{wd_idx}"
                # Вычисляем дату этого дня недели на текущей неделе
                target_date = target_date - datetime.timedelta(days=target_date.weekday()) + datetime.timedelta(days=wd_idx)
                break
    
    # Форматируем дату для поиска в БД
    date_str = target_date.strftime("%Y-%m-%d")
    date_human = target_date.strftime("%d.%m")
    
    try:
        events = get_events_for_date(date_str)
        
        if not events:
            text = f"На {date_human} у вас нет никаких запланированных дел. Отдыхайте!"
        else:
            text = f"Ваше расписание на {date_human}:\n"
            for ev in events:
                # Извлекаем поля: event_time, title, event_type, room, notes 
                time_str = ev[0]
                title = ev[1]
                text += f"В {time_str} — {title}.\n"
                
    except Exception as e:
        print(f"Ошибка БД: {e}")
        text = "Извините, сейчас я не могу получить доступ к вашему расписанию. База данных недоступна."
        
    return {
        "text": text,
        "end_session": False,
        "intent": intent
    }
