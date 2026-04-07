import requests
from bs4 import BeautifulSoup
import re
from typing import List, Dict, Any

def fetch_nstu_schedule(group_name: str) -> List[Dict[str, Any]]:
    """
    Парсит расписание занятий университета НГТУ.
    
    :param group_name: Название группы, например 'АВТ-11'
    :return: Список словарей с занятиями (день, время, тип недели, предмет, аудитория)
    """
    url = f"https://www.fb.nstu.ru/study_process/schedule/schedule_classes/schedule?group={group_name}&print=true"
    
    response = requests.get(url)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, "lxml")
    
    schedule = []
    current_day = None
    
    # Находим главный контейнер
    table_body = soup.find("div", class_="schedule__table-body")
    if not table_body:
        return schedule
        
    rows = table_body.find_all("div", class_="schedule__table-row")
    
    for row in rows:
        # Проверяем наличие дня недели
        day_elem = row.find("div", class_="schedule__table-day")
        if day_elem and day_elem.text.strip():
            current_day = day_elem.text.strip()
            
        time_elem = row.find("div", class_="schedule__table-time")
        item_elem = row.find("div", class_="schedule__table-item")
        class_elem = row.find("div", class_="schedule__table-class")
        
        if time_elem and item_elem:
            time_text = time_elem.text.strip()
            item_text = item_elem.text.strip()
            class_text = class_elem.text.strip() if class_elem else ""
            
            # Разделяем текст предмета и типа недели
            week_type = ""
            subject = item_text
            
            # Ищем маркеры недели (по чётным, по нечётным, недели 4 8 12 и т.д.)
            # Простое регулярное выражение для поиска типичных паттернов в начале строки
            week_pattern = re.compile(r'^(по\s+чётным|по\s+нечётным|недели[\s\d,]+)\s*(.*)', re.IGNORECASE)
            match = week_pattern.match(item_text)
            
            if match:
                week_type = match.group(1).strip()
                subject = match.group(2).strip()
                
            schedule.append({
                "day": current_day,
                "time": time_text,
                "week_type": week_type,
                "subject": subject,
                "room": class_text
            })
            
    return schedule
