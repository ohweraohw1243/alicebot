import requests
from bs4 import BeautifulSoup
import re
from typing import List, Dict, Any

def is_class_this_week(week_type: str, current_week: int) -> bool:
    """
    Проверяет, должна ли пара проводиться на текущей неделе.
    """
    if not week_type or not current_week:
        return True
        
    wt = week_type.lower()
    
    if "нечётным" in wt:
        return current_week % 2 != 0
    elif "чётным" in wt:
        return current_week % 2 == 0
    elif "недели" in wt:
        weeks = [int(x) for x in re.findall(r'\d+', wt)]
        if weeks:
            return current_week in list(weeks)
            
    return True

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
    current_time = None
    
    # Находим главный контейнер
    table_body = soup.find("div", class_="schedule__table-body")
    if not table_body:
        return schedule
        
    # Ищем текущую учебную неделю с главной страницы, так как на print=true ее нет
    current_week = None
    try:
        main_url = f"https://www.fb.nstu.ru/study_process/schedule/schedule_classes/schedule?group={group_name}"
        main_response = requests.get(main_url)
        week_match = re.search(r'(\d+)\s+учебная неделя', main_response.text)
        if week_match:
            current_week = int(week_match.group(1))
    except Exception:
        pass
        
    rows = table_body.find_all("div", class_="schedule__table-row")
    
    for row in rows:
        # Проверяем наличие дня недели
        day_elem = row.find("div", class_="schedule__table-day")
        if day_elem and day_elem.text.strip():
            current_day = day_elem.text.strip()
            
        time_elem = row.find("div", class_="schedule__table-time")
        if time_elem and time_elem.text.strip():
            current_time = time_elem.text.strip()
            
        item_elem = row.find("div", class_="schedule__table-item")
        class_elem = row.find("div", class_="schedule__table-class")
        
        if current_time and item_elem:
            time_text = current_time
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
                
            # Убираем ФИО преподавателя (всё, что после символа "·")
            if '·' in subject:
                subject = subject.split('·')[0].strip()
                
            # Проверяем, подходит ли пара под номер текущей недели
            if current_week and not is_class_this_week(week_type, current_week):
                continue
                
            event = {
                "day": current_day,
                "time": time_text,
                "week_type": week_type,
                "subject": subject,
                "room": class_text
            }
            
            if event not in schedule:
                schedule.append(event)
            
    return schedule
