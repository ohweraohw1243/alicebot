-- Таблица для хранения событий расписания
CREATE TABLE IF NOT EXISTS events (
    id VARCHAR PRIMARY KEY,
    event_date DATE NOT NULL,
    event_time VARCHAR NOT NULL,
    title VARCHAR NOT NULL,
    event_type VARCHAR,
    duration_min INTEGER,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица для логирования запросов от Алисы
CREATE TABLE IF NOT EXISTS alice_request_log (
    id SERIAL PRIMARY KEY,
    request_id VARCHAR,
    utterance TEXT,
    intent VARCHAR,
    response TEXT,
    requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
