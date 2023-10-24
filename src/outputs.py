import csv
import datetime as dt
import logging

from prettytable import PrettyTable

from constants import DATETIME_FORMAT, PRETTY, FILE, RESULTS_DIR, BASE_DIR


def control_output(results, cli_args):
    output = cli_args.output
    if output == PRETTY:
        pretty_output(results)
    elif output == FILE:
        file_output(results, cli_args)
    else:
        default_output(results)


def default_output(results):
    for row in results:
        print(*row)


def pretty_output(results):
    table = PrettyTable()
    table.field_names = results[0]
    table.align = 'l'
    table.add_rows(results[1:])
    print(table)


def file_output(results, cli_args):
    results_dir = BASE_DIR / 'results'
    results_dir.mkdir(exist_ok=True)
    # RESULTS_DIR.mkdir(exist_ok=True)
    # если сделать через константу валятся тесты

    parser_mode = cli_args.mode
    now = dt.datetime.now()
    now_formatted = now.strftime(DATETIME_FORMAT)

    file_name = f'{parser_mode}_{now_formatted}.csv'
    file_path = results_dir / file_name
    with open(file_path, 'w', encoding='utf8') as f:
        writer = csv.writer(f, dialect='unix')
        writer.writerow(results)
    logging.info(f'Файл с результатами был сохранён: {file_path}')
