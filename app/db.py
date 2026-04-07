import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    """
    Создает и возвращает подключение к PostgreSQL (Supabase).
    Данные берутся из переменных окружения.
    """
    return psycopg2.connect(
        host=os.getenv("SUPABASE_HOST", "db.nzcarrvtenhknxuwvono.supabase.co"),
        port=os.getenv("SUPABASE_PORT", "5432"),
        database=os.getenv("SUPABASE_DB", "postgres"),
        user=os.getenv("SUPABASE_USER", "postgres"),
        password=os.getenv("SUPABASE_PASSWORD", "")
    )

def get_events_for_date(target_date: str) -> list:
    """
    Получает расписание на определенную дату (формат YYYY-MM-DD).
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            query = """
                SELECT event_time, title, event_type, notes 
                FROM events 
                WHERE event_date = %s
                ORDER BY event_time
            """
            cur.execute(query, (target_date,))
            return cur.fetchall()
    finally:
        conn.close()

def log_alice_request(request_id: str, utterance: str, intent: str, response: str):
    """
    Логирует запрос от Алисы и выданный ответ.
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            query = """
                INSERT INTO alice_request_log (request_id, utterance, intent, response)
                VALUES (%s, %s, %s, %s)
            """
            cur.execute(query, (request_id, utterance, intent, response))
        conn.commit()
    except Exception as e:
        print(f"Ошибка логирования запроса: {e}")
    finally:
        conn.close()
