from fastapi import FastAPI, Request
from app.handler import process_alice_request
from app.db import log_alice_request

app = FastAPI(title="AliceSchedule Webhook", description="Алиса Навык для планировщика расписания")

@app.get("/")
async def health_check():
    """
    Эндпоинт для проверки активности сервера (ping).
    Полезен для предотвращения "засыпания" бесплатного сервера на Render.
    """
    return {"status": "ok", "app": "AliceSchedule"}

@app.post("/alice")
async def alice_endpoint(request: Request):
    """
    Основной эндпоинт навыка Яндекс Алиса.
    Принимает POST-запрос с JSON и возвращает ответ.
    """
    data = await request.json()
    session = data.get("session", {})
    req = data.get("request", {})
    version = data.get("version", "1.0")
    
    request_id = session.get("message_id", "")
    utterance = req.get("command", "")
    
    # Обрабатываем бизнес-логику и подготавливаем ответ
    result = process_alice_request(data)
    
    text_response = result["text"]
    intent = result["intent"]
    
    # Логируем запрос пользователя и свой ответ в ClickHouse
    log_alice_request(str(request_id), utterance, intent, text_response)
    
    return {
        "version": version,
        "session": session,
        "response": {
            "text": text_response,
            "end_session": result["end_session"]
        }
    }
