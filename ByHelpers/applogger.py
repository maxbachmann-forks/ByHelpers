import logging
from logging import config as logging_config
import os

logger = None
APP_NAME = os.getenv('APP_NAME', 'applogger')
ENVIRONMENT = os.getenv('ENV', 'LOCAL')
REGION = os.getenv('REGION', 'MEX')
TARGET = os.getenv('TARGET')

LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_INFO_FILE = os.getenv('LOG_INFO_FILE')
LOG_ERROR_FILE = os.getenv('LOG_ERROR_FILE')
LOG_HANDLERS = os.getenv('LOG_HANDLERS', ['console', 'info_file_handler', 'error_file_handler', 'fluent_async_handler'])


app_logging_config = {
    'version': 1,
    'loggers': {
        '': {  # root logger
            'level': 'NOTSET',
            'handlers': ['console', 'info_file_handler', 'error_file_handler'],
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'formatter': 'info',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
        },
        'info_file_handler': {
            'level': 'INFO',
            'formatter': 'info',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '../logs/application_name_info.log',
            'mode': 'a',
            'maxBytes': 1048576,
            'backupCount': 10
        },
        'error_file_handler': {
            'level': 'WARNING',
            'formatter': 'error',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '../logs/application_name_error.log',
            'mode': 'a',
            'maxBytes': 1048576,
            'backupCount': 10
        },
        'fluent_async_handler': {
            'level': 'INFO',
            'class': 'fluent.handler.FluentHandler',
            'host': '0.0.0.0',
            'port': 24224,
            'tag': 'app.dynamic_app_tag',
            'buffer_overflow_handler': 'overflow_handler',
            # 'queue_circular': True,
            'formatter': 'night_watch'

        }
    },
    'formatters': {
        'info': {
            'format': '%(asctime)s-%(module)s-%(lineno)s::%(levelname)s:: %(message)s'
        },
        'error': {
            'format': '%(asctime)s-%(module)s-%(lineno)s::%(levelname)s:: %(message)s'
        },
        'night_watch': {
            '()': 'fluent.handler.FluentRecordFormatter',
            'format': {
                'time': '%(asctime)s',
                'level': '%(levelname)s',
                'hostname': '%(hostname)s',
                'where': '%(module)s-%(lineno)s',
            }
        }
    },

}


def create_logger(name=APP_NAME):
    global logger

    log_level = LOG_LEVEL
    app_logging_config['loggers']['']['handlers'] = list(LOG_HANDLERS)

    if log_level is not None and log_level in ['NOTSET', 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
        print('Changing LOG_LEVEL={} for console, info_file_handler and fluent_async_handler'.format(log_level))
        app_logging_config['handlers']['console']['level'] = log_level
        app_logging_config['handlers']['info_file_handler']['level'] = log_level
        app_logging_config['handlers']['fluent_async_handler']['level'] = log_level

    log_info_file = LOG_INFO_FILE
    if log_info_file is None or log_info_file == '':
        log_info_file = os.path.join(os.getcwd(), 'logs', APP_NAME + '_info.log')
    if TARGET is not None:
        log_info_file = log_info_file.replace('.log', '_' + TARGET + '.log')
    print('LOG_INFO_FILE={}'.format(log_info_file))
    app_logging_config['handlers']['info_file_handler']['filename'] = log_info_file

    log_error_file = LOG_ERROR_FILE
    if log_error_file is None or log_error_file == '':
        log_error_file = os.path.join(os.getcwd(), 'logs', APP_NAME + '_error.log')
    if TARGET is not None:
        log_error_file = log_error_file.replace('.log', '_' + TARGET + '.log')
    print('ERROR_INFO_FILE={}'.format(log_error_file))
    app_logging_config['handlers']['error_file_handler']['filename'] = log_error_file

    app_logging_config['handlers']['fluent_async_handler']['tag'] = APP_NAME + '.' + ENVIRONMENT + '.' + REGION

    app_logging_config['formatters']['night_watch']['format']['hostname'] = \
        app_logging_config['handlers']['fluent_async_handler']['tag']

    logging_config.dictConfig(app_logging_config)
    logger = logging.getLogger(name)
    logger.debug(app_logging_config)


def get_logger():
    return logging.getLogger(APP_NAME)


if __name__ == '__main__':
    create_logger(APP_NAME)
    logger = get_logger()
    logger.debug('Debug message')
    logger.info('Info message')
    logger.warning('Warning message sent')
    logger.error('Error message sent')
    logger.critical('Critical message sent')
