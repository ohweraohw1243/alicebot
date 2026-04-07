import requests
from typing import List, Dict, Any
from datetime import datetime, timedelta

def fetch_moyklass_schedule(
    date_from: str, 
    date_to: str, 
    filial_id: str, 
    room_id: str, 
    teacher_id: str, 
    connect_sid: str, 
    device_id: str, 
    version: str,
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
) -> List[Dict[str, Any]]:
    """
    Получает расписание из CRM МойКласс через внутреннее API.
    
    :param date_from: Начальная дата в формате YYYY-MM-DD
    :param date_to: Конечная дата в формате YYYY-MM-DD
    ...
    """
    url = "https://app.moyklass.com/api/crm/lesson/schedule"
    
    params = {
        "dateFrom": date_from,
        "dateTo": date_to,
        "limit": 50,
        "offset": 0,
        "filial_id": filial_id,
        "room_id": room_id,
        "teacher_id": teacher_id
    }
    
    cookies = {
        "connect.sid": connect_sid,
        "device_id": device_id,
        "version": version
    }
    
    headers = {
        "User-Agent": user_agent
    }
    
    response = requests.get(url, params=params, cookies=cookies, headers=headers)
    response.raise_for_status()
    
    data = response.json()
    schedule = []
    
    for item in data:
        # Проверяем, не отменено ли занятие 
        # (в МойКласс отмененные занятия обычно имеют статус `statusId` = 3 или `status` 'canceled')
        status_id = item.get("statusId")
        if status_id == 3 or str(item.get("status", "")).lower() == "canceled":
            continue

        lesson_id = str(item.get("id"))
        raw_date = item.get("date")          # "YYYY-MM-DD"
        raw_begin = item.get("begin_time")   # "HH:MM" или "HH:MM:SS"
        raw_end = item.get("end_time")
        
        # Переводим время из МСК в Новосибирск (+4 часа)
        try:
            dt_begin = datetime.strptime(f"{raw_date} {raw_begin[:5]}", "%Y-%m-%d %H:%M")
            dt_begin_nsk = dt_begin + timedelta(hours=4)
            date = dt_begin_nsk.strftime("%Y-%m-%d")
            begin_time = dt_begin_nsk.strftime("%H:%M")
            
            if raw_end:
                dt_end = datetime.strptime(f"{raw_date} {raw_end[:5]}", "%Y-%m-%d %H:%M")
                dt_end_nsk = dt_end + timedelta(hours=4)
                end_time = dt_end_nsk.strftime("%H:%M")
            else:
                end_time = raw_end
        except Exception:
            # Если формат другой - оставляем как есть
            date, begin_time, end_time = raw_date, raw_begin, raw_end
        
        # Название предмета
        subject_name = item.get("Class", {}).get("name", "Неизвестный предмет")
        
        # Очищаем название от лишних деталей (например, "Стандарт 2 раза в неделю")
        import re
        subject_name = re.sub(r'(\s+(Стандарт|Индивидуально|Группа))?(\s*\d+\s*(раз|раза|занятие|занятия)\s*в\s*неделю.*)?', '', subject_name, flags=re.IGNORECASE).strip()
        
        # Имена учеников
        students = []
        for record in item.get("LessonRecords", []):
            student_name = record.get("User", {}).get("name")
            if student_name:
                students.append(student_name)
        
        # Склеиваем название
        students_str = ", ".join(students)
        full_title = f"{subject_name} ({students_str})" if students else subject_name
        
        schedule.append({
            "id": lesson_id,
            "date": date,
            "begin_time": begin_time,
            "end_time": end_time,
            "title": full_title
        })
        
    return schedule
