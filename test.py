from urllib.parse import urljoin
import requests_cache

from bs4 import BeautifulSoup
from tqdm import tqdm

from utils import get_response, find_tag
from exceptions import ParserFindTagException

mismatched_statuses = []


def compare(status_type: str,
            status: str,
            type: str,
            pep_page_url: str):

    intable_status_type = status_type.split(', ')
    table_status = intable_status_type[1]
    print(table_status)
    table_type = intable_status_type[0]
    print(table_type)
    print(status)
    print(type)
    print()
    if table_status != status or table_type != type:
        print()
        print('comparement!!!')
        print()
        mismatched_statuses.append([pep_page_url,
                                    table_status,
                                    table_type,
                                    status,
                                    type])
    return


def pep(session):
    pep_url = 'https://peps.python.org/'
    response = get_response(session, pep_url)
    if response is None:
        return
    soup = BeautifulSoup(response.text, features='lxml')
    tables = soup.find_all('tbody')
    for table in tqdm(tables):
        rows = table.find_all("tr")
        for row in tqdm(rows):
            try:
                a_tag = find_tag(row,
                                 'a',
                                 attrs={'class': 'pep reference internal'})
                first_col = find_tag(row, 'td')
                table_status_type = find_tag(first_col, 'abbr')
                pg_pep_url = urljoin(pep_url, a_tag['href'])
                response = get_response(session,
                                        pg_pep_url)
                soup = BeautifulSoup(response.text, features='lxml')
                pep_content = find_tag(soup,
                                       "section",
                                       attrs={"id": "pep-content"})
                dl = find_tag(pep_content, 'dl')
                status_type = dl.find_all("abbr")
                compare(table_status_type['title'],
                        status_type[0].text,
                        status_type[1].text,
                        pg_pep_url)
            except ParserFindTagException:
                continue
    if len(mismatched_statuses) > 0:
        print(mismatched_statuses)
session = requests_cache.CachedSession()
pep(session)