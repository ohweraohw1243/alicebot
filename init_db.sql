CREATE DATABASE IF NOT EXISTS schedule;

-- Таблица для хранения событий расписания
CREATE TABLE IF NOT EXISTS schedule.events (
    id String,
    event_date Date,
    event_time String,
    title String,
    event_type String,
    duration_min Int32,
    notes String,
    created_at DateTime DEFAULT now()
) ENGINE = MergeTree()
ORDER BY (event_date, event_time);

-- Таблица для логирования запросов от Алисы
CREATE TABLE IF NOT EXISTS schedule.alice_request_log (
    request_id String,
    utterance String,
    intent String,
    response String,
    requested_at DateTime DEFAULT now()
) ENGINE = MergeTree()
ORDER BY requested_at;
