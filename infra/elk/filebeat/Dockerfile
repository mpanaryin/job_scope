FROM docker.elastic.co/beats/filebeat:8.17.3

USER root

# Копируем конфиг и скрипт
COPY filebeat.yml /usr/share/filebeat/filebeat.yml
COPY entrypoint.sh /usr/local/bin/entrypoint.sh

# Назначаем права
RUN chmod go-w /usr/share/filebeat/filebeat.yml \
    && chmod +x /usr/local/bin/entrypoint.sh

USER filebeat

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
