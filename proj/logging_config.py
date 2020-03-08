import os

simple_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
complex_format = (
    '%(asctime)s - %(name)s - %(levelname)s'
    ' - %(module)s : %(lineno)d - %(message)s'
)

logging_config = {
    "version": 1,
    "disable_existing_loggers": False,
    'formatters': {
        'simple': {
            'format': simple_format
        },
        'complex': {
            'format': complex_format
        },
    },
    "handlers": {
        'file': {
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': 'proj/logs/api.log',
            'when': 'midnight',
            'interval': 1,
            'backupCount': 50,
            'formatter': 'complex',
        },
        "console": {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    "loggers": {
        '': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
