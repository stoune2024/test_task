import logging
from logging.config import dictConfig
import json
from datetime import datetime


class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            'timestamp': datetime.now(),
            'level': record.levelname,
            'logger': record.name,
            'module': record.module,
            'line': record.lineno,
            'message': record.getMessage()
        }
        if record.exc_info:
            log_record['exception'] = self.formatException(record.exc_info)
        return json.dumps(log_record)


log_config = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'json': {
            '()': JsonFormatter
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'json',
            'stream': 'ext://sys.stdout',
        },
        'rotating_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'INFO',
            'formatter': 'json',
            'filename': 'logs/fastapi.log',
            'maxBytes': 1048521,  # 1MB
            'backupCount': 5,
        },
    },
    'loggers': {
        'fastapi': {
            'handlers': ['rotating_file'],
            'level': 'INFO',
            'propagate': False
        },
    },
    'root': {'handlers': ['console'], 'level': 'INFO'},
}

dictConfig(log_config)

fastapi_logger = logging.getLogger('fastapi')