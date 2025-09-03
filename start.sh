#!/bin/bash
# Скрипт запуска FastAPI на Render

# В Render автоматически назначается порт через $PORT
# Если PORT не задан, используем 8000
: "${PORT:=8000}"

# Запуск uvicorn с перезагрузкой отключено (production)
uvicorn main:app --host 0.0.0.0 --port $PORT
