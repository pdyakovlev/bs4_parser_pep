import logging
from typing import List

from requests import RequestException

from exceptions import ParserFindTagException


def get_response(session, url):
    try:
        response = session.get(url)
        response.encoding = 'utf-8'
        return response
    except RequestException:
        logging.exception(
            f'Возникла ошибка при загрузке страницы {url}',
            stack_info=True
        )


def find_tag(soup, tag, attrs=None):
    searched_tag = soup.find(tag, attrs=(attrs or {}))
    if searched_tag is None:
        error_msg = f'Не найден тег {tag} {attrs}'
        logging.error(error_msg, stack_info=True)
        raise ParserFindTagException(error_msg)
    return searched_tag


def log_mismatches(mismatches: List) -> None:
    """Функция логирующая несовпадение статусов документа в источниках"""
    mismatches_info_string = "\nНесовпадающие статусы:\n"
    for mis in mismatches:
        mismatches_info_string += (f"{mis[0]}\n"
                                   f"Статус в карточке: {mis[1]}\n"
                                   f"Тип в карточке: {mis[2]}\n"
                                   f"Ожидаемые статусы: {mis[3]}\n")
    if len(mismatches) > 0:
        logging.info(mismatches_info_string)
