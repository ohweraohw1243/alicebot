import os
import clickhouse_connect
from dotenv import load_dotenv

load_dotenv()

def get_client():
    """
    Создает и возвращает подключение к ClickHouse.
    Данные берутся из переменных окружения.
    """
    return clickhouse_connect.get_client(
        host=os.getenv("CH_HOST", "localhost"),
        port=int(os.getenv("CH_PORT", 8123)),
        username=os.getenv("CH_USER", "default"),
        password=os.getenv("CH_PASSWORD", "")
    )

def get_events_for_date(target_date: str) -> list:
    """
    Получает расписание на определенную дату (формат YYYY-MM-DD).
    """
    client = get_client()
    query = f"""
        SELECT event_time, title, event_type, notes 
        FROM schedule.events 
        WHERE event_date = '{target_date}'
        ORDER BY event_time
    """
    result = client.query(query)
    return result.result_rows

def log_alice_request(request_id: str, utterance: str, intent: str, response: str):
    """
    Логирует запрос от Алисы и выданный ответ.
    """
    client = get_client()
    
    data = [[request_id, utterance, intent, response]]
    columns = ['request_id', 'utterance', 'intent', 'response']
    
    try:
        client.insert('schedule.alice_request_log', data, column_names=columns)
    except Exception as e:
        print(f"Ошибка логирования запроса: {e}")
