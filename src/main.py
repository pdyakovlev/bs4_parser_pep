import logging
import re
from typing import List, Union
from urllib.parse import urljoin

import requests_cache
from tqdm import tqdm

from configs import configure_argument_parser, configure_logging
from constants import MAIN_DOC_URL, PEP_BASE_URL, BASE_DIR
from exceptions import ParserFindTagException
from outputs import control_output
from utils import find_tag, get_response, log_mismatches, get_soup


def whats_new(session):
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')
    results = [('Ссылка на статью', 'Заголовок', 'Редактор, Автор')]
    response = get_response(session, whats_new_url)
    if response is None:
        return None
    soup = get_soup(response)
    main_div = find_tag(soup, 'section',
                        attrs={'id': 'what-s-new-in-python'})
    div_with_ul = find_tag(main_div, 'div',
                           attrs={'class': 'toctree-wrapper'})
    sections_by_python = div_with_ul.find_all(
        'li', attrs={'class': 'toctree-l1'})
    for section in tqdm(sections_by_python):
        version_a_tag = find_tag(section, 'a')
        version_link = urljoin(whats_new_url, version_a_tag['href'])
        response = get_response(session, version_link)
        if response is None:
            continue
        soup = get_soup(response)
        h1 = find_tag(soup, 'h1')
        dl = find_tag(soup, 'dl')
        dl_text = dl.text.replace('\n', ' ')
        results.append(
            (version_link, h1.text, dl_text)
        )
    return results


def latest_versions(session):
    results = [('Ссылка на документацию', 'Версия', 'Статус')]
    response = get_response(session, MAIN_DOC_URL)
    if response is None:
        return None
    soup = get_soup(response)
    sidebar = find_tag(soup, 'div',
                       attrs={"class": "sphinxsidebarwrapper"})
    ul_tags = sidebar.find_all('ul')
    for ul in ul_tags:
        if 'All versions' in ul.text:
            a_tags = ul.find_all('a')
            break
        raise ParserFindTagException('Ничего не нашлось')
    pattern = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'
    for a_tag in a_tags:
        link = a_tag['href']
        text_match = re.search(pattern, a_tag.text)
        if text_match is not None:
            version, status = text_match.groups()
        else:
            version, status = a_tag.text, ''
        results.append((link, version, status))
    return results


def download(session):
    downloads_url = urljoin(MAIN_DOC_URL, 'download.html')
    response = get_response(session, downloads_url)
    if response is None:
        return
    soup = get_soup(response)
    table = find_tag(soup, 'table', attrs={"class": "docutils"})
    pdf_a4_tag = find_tag(table, 'a',
                          {'href': re.compile(r'.+pdf-a4\.zip$')})
    archive_url = urljoin(downloads_url, pdf_a4_tag['href'])
    filename = archive_url.split('/')[-1]
    downloads_dir = BASE_DIR / 'downloads'
    downloads_dir.mkdir(exist_ok=True)
    # DOWNLOADS_DIR.mkdir(exist_ok=True)
    # если сделать через константу валятся тесты,
    # решение без констант из теоритической части и,
    # видимо зашито в логике тестов
    archive_dir = downloads_dir / filename
    response = get_response(session, archive_url)
    with open(archive_dir, 'wb') as file:
        file.write(response.content)
    logging.info(f'Архив был загружен и сохранён: {archive_dir}')


def compare_statuses(table_status_type: str,
                     status: str,
                     type: str,
                     pep_page_url: str,
                     mismatches: List) -> None:
    """Функция сравнения статуса на сранице документа со статусом в таблице."""
    t_status_type = table_status_type.split(", ")
    if status not in t_status_type or type not in t_status_type:
        mismatches.append([pep_page_url, status, type, table_status_type])


def pep(session) -> Union[List, None]:
    # Счётчик числа документов
    total_counter: int = 0
    # Список для результатов
    results: List = [('Статус', 'Количество')]
    # Список для записи несовпадений статусов документов
    mismatches: List = []
    # Словарь для записи статусов и количества документов с данным статусом
    statuses: dict = {}
    # Список ссылок на проверенные документы
    pg_pep_urls: List = []

    response = get_response(session, PEP_BASE_URL)

    if response is None:
        return None
    soup = get_soup(response)
    # Получаем список таблиц
    tables = soup.find_all('tbody')
    for table in tqdm(tables):
        # Получаем список строк
        rows = table.find_all("tr")
        for row in rows:
            try:
                # Получаем первую ссылку на документ для каждой строки
                a_tag = find_tag(row,
                                 'a',
                                 attrs={'class': 'pep reference internal'})

                pg_pep_url = urljoin(PEP_BASE_URL, a_tag['href'])
                # Проверка на проверенность ссылки ранее,
                # если документ по ссылке уже проверялся
                # переходим на новую строку
                if pg_pep_url not in pg_pep_urls:
                    # Получаем первую колонку в строке
                    first_col = find_tag(row, 'td')
                    # Получаем элемент со статусом и типом из таблицы
                    table_status_type = find_tag(first_col, 'abbr')
                    # Посылаем запрос на страницу документа
                    response = get_response(session,
                                            pg_pep_url)
                    soup = get_soup(response)
                    # Получаем элемент с текстом документа
                    pep_content = find_tag(soup,
                                           "section",
                                           attrs={"id": "pep-content"})
                    # Получаем элемент с информацией о документе
                    dl = find_tag(pep_content, 'dl')
                    # Получаем элементы с информацией о статусе и типе
                    status_type = dl.find_all("abbr")
                    # Если документ с таким статусом не встречался ранее:
                    if status_type[0].text not in statuses.keys():
                        # Записываем в словарь статус, число вхождений = 1,
                        # повышаем общее число документов на 1
                        statuses[status_type[0].text] = 1
                        total_counter += 1
                    else:
                        # Иначе повышаем число вхождений документов
                        # с подобным статусом и общее число документов на 1
                        statuses[status_type[0].text] += 1
                        total_counter += 1
                    # Добавляем проверенную ссылку в список
                    pg_pep_urls.append(pg_pep_url)
                    # Сравниваем статусы в таблице и на странице документа
                    compare_statuses(table_status_type["title"],
                                     status_type[0].text,
                                     status_type[1].text,
                                     pg_pep_url,
                                     mismatches)
            except ParserFindTagException:
                continue
    # Записываем значения в результат
    for key, val in statuses.items():
        results.append([key, val])
    results.append(["Total", total_counter])
    # Вызываем логгирование несоответствий
    log_mismatches(mismatches)
    return results


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep,
}


def main():
    try:
        configure_logging()
        logging.info('Парсер запущен.')
        arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
        args = arg_parser.parse_args()
        logging.info(f'Аргументы командной строки: {args}')
        session = requests_cache.CachedSession()
        if args.clear_cache:
            session.cache.clear()
        parser_mode = args.mode
        results = MODE_TO_FUNCTION[parser_mode](session)
        if results is not None:
            control_output(results, args)
        logging.info('Парсер завершил работу.')
    except Exception:
        logging.exception(
            'Возникла ошибка при выполнении',
            stack_info=True
        )


if __name__ == '__main__':
    main()
