import requests
from typing import List, Dict, Any

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
        # Извлекаем основные поля
        lesson_id = item.get("id")
        date = item.get("date")
        begin_time = item.get("begin_time")
        end_time = item.get("end_time")
        
        # Название предмета
        subject_name = item.get("Class", {}).get("name", "Неизвестный предмет")
        
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
