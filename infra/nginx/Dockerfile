# nginx/Dockerfile
FROM nginx:latest

# Копируем шаблон конфигурационного файла в контейнер
COPY nginx.test.conf.template /etc/nginx/nginx.test.conf.template
COPY nginx.dev.conf.template /etc/nginx/nginx.dev.conf.template
COPY nginx.prod.conf.template /etc/nginx/nginx.prod.conf.template

# Копируем entrypoint-скрипт
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Задаём точку входа, которая подставит переменные и запустит nginx в foreground режиме
ENTRYPOINT ["/entrypoint.sh"]