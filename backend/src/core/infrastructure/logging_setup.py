"""
Logging configuration module.

This module sets up logging automatically upon import using `logging.config.dictConfig`.
It defines both stream (stdout) and rotating file handlers with JSON and plain formats.

To activate logging, simply import:
    import src.core.infrastructure.logging_setup

No functions need to be called explicitly — importing is enough to configure logging globally.
"""

import os
import logging.config


LOG_DIR = "/app/logs"
log_file = os.path.join(LOG_DIR, "app.log")


class LogMessageFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        message_templates = []
        return not any([True for template in message_templates if template in record.getMessage()])


LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'standard': {
            'format': '[%(asctime)s] [%(levelname)s] %(name)s: %(message)s'
        },
        "json": {
            "()": "pythonjsonlogger.json.JsonFormatter",
            "format": "%(asctime)s %(levelname)s %(message)s %(exc_info)s %(name)s %(filename)s "
                      "%(funcName)s %(lineno)d %(process)d %(threadName)s",
            "rename_fields": {
                "asctime": "@timestamp",
                "levelname": "log.level",
                "message": "message",
                "exc_info": "error.stack_trace",
                "name": "log.logger",
                "filename": "log.origin.file.name",
                "funcName": "log.origin.function",
                "lineno": "log.origin.line",
                "process": "process.pid",
                "threadName": "thread.name"
            },
            "datefmt": "%d-%m-%Y %H:%M:%S"
        },
        "full_json": {
            "()": "pythonjsonlogger.json.JsonFormatter",
            "format": "%(asctime)s %(created)f %(filename)s %(funcName)s %(levelname)s %(levelno)s "
                      "%(lineno)d %(message)s %(module)s %(msecs)d %(name)s %(pathname)s %(process)d "
                      "%(processName)s %(relativeCreated)d %(thread)d %(threadName)s %(exc_info)s",
            "rename_fields": {
                "asctime": "@timestamp",
                "levelname": "log.level",
                "levelno": "log.level_no",
                "message": "message",
                "exc_info": "error.stack_trace",
                "name": "log.logger",
                "filename": "log.origin.file.name",
                "funcName": "log.origin.function",
                "lineno": "log.origin.line",
                "process": "process.pid",
                "threadName": "thread.name",
                "pathname": "log.origin.file.path",
                "module": "log.origin.module",
                "processName": "process.name",
                "created": "event.created",
                "relativeCreated": "event.relative_created",
                "msecs": "event.milliseconds",
                "thread": "thread.id"
            },
            "datefmt": "%d-%m-%Y %H:%M:%S"
        },
    },
    'handlers': {
        'stream_standard_handler': {
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',  # Default is stderr
        },
        'stream_json_handler': {
            'formatter': 'json',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
        },
        'file_handler': {
            'formatter': 'json',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': log_file,
            'maxBytes': 1024 * 1024 * 1,  # = 1MB
            'backupCount': 3,
        },
    },
    'filters': {
        'message_filter': {
            '()': LogMessageFilter,
        },
    },
    'loggers': {
        "root": {
            "level": "INFO",
            "handlers": ["stream_standard_handler", "file_handler"],
            'filters': ['message_filter'],
            "propagate": False,
        },
        'uvicorn': {
            'handlers': ['stream_standard_handler', 'file_handler'],
            'filters': ['message_filter'],
            'level': 'INFO',
            'propagate': False
        },
        'uvicorn.access': {
            'handlers': ['stream_standard_handler', 'file_handler'],
            'filters': ['message_filter'],
            'level': 'INFO',
            'propagate': False
        },
        'uvicorn.error': {
            'handlers': ['stream_standard_handler', 'file_handler'],
            'filters': ['message_filter'],
            'level': 'INFO',
            'propagate': False
        },
        'uvicorn.asgi': {
            'handlers': ['stream_standard_handler', 'file_handler'],
            'filters': ['message_filter'],
            'level': 'INFO',
            'propagate': False
        },
        'celery': {
            'handlers': ['stream_standard_handler', 'file_handler'],
            'filters': ['message_filter'],
            'level': 'INFO',
            'propagate': False
        },
        'celery.worker': {
            'handlers': ['stream_standard_handler', 'file_handler'],
            'filters': ['message_filter'],
            'level': 'INFO',
            'propagate': False
        },
    },
}


logging.config.dictConfig(LOGGING_CONFIG)
