import argparse
import logging
from logging.handlers import RotatingFileHandler
from constants import (LOGS_FORMAT,
                       DATETIME_FORMAT,
                       PRETTY, FILE,
                       LOG_DIR,
                       LOG_FILE)


def configure_argument_parser(available_modes):
    parser = argparse.ArgumentParser(description='Парсер документации Python')
    parser.add_argument(
        'mode',
        choices=available_modes,
        help='Режимы работы парсера'
    )
    parser.add_argument(
        '-c',
        '--clear-cache',
        action='store_true',
        help='Очистка кеша'
    )
    parser.add_argument(
        '-o',
        '--output',
        choices=(PRETTY, FILE),
        help='Дополнительные способы вывода данных'
    )
    return parser


def configure_logging():
    LOG_DIR.mkdir(exist_ok=True)
    rotating_handler = RotatingFileHandler(LOG_FILE,
                                           maxBytes=10**6,
                                           backupCount=5,
                                           encoding='utf8')
    logging.basicConfig(
        datefmt=DATETIME_FORMAT,
        format=LOGS_FORMAT,
        level=logging.INFO,
        handlers=(rotating_handler, logging.StreamHandler())
    )
