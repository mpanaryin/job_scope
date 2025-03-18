#!/bin/sh
set -e

echo "Запуск приложения..."
exec uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload