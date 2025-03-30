#!/bin/bash
# Запуск без лишних флагов

# запускает Filebeat в foreground и пишет логи в stdout (а не файл).
exec filebeat -e
