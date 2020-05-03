import csv
import os
import shutil

import requests
from bs4 import BeautifulSoup
from celery import Celery
from celery.schedules import crontab
from slack_webhook import Slack

url = 'https://hh.ru/search/vacancy?search_period=7&clusters=true&enable_snippets=true&text='

search_combinations = (
    'data+scientist',
    'data+engineer',
    'big+data',
    'deep+learning',
)

user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) ' \
             'Chrome/35.0.1916.47 Safari/537.36'

app = Celery('periodic', broker=os.environ.get('CELERY_BROKER_URL', 'redis://:secret_password@redis:6379/'))


def get_soup(soup_url):
    response = requests.get(soup_url, headers={'User-Agent': user_agent})
    return BeautifulSoup(response.content, 'html.parser')


def get_vacancies(soup, vacancies_urls, new_vacancies_count):
    vacancies = soup.select('span.resume-search-item__name > span.g-user-content > a')

    for vacancy in vacancies:
        vacancies_urls.append(vacancy['href'])
        new_vacancies_count += 1

    return new_vacancies_count


def get_employers_statistic(soup, employers_dict):
    employers = soup.select('div.vacancy-serp-item__meta-info > a')

    for employer in employers:
        text = employer.text.lstrip()
        if text == '':
            continue
        if text in employers_dict:
            employers_dict[text] += 1
        else:
            employers_dict[text] = 1

    return employers_dict


def write_data(path, data):
    with open(path, 'w') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerows(data)


def create_dir(path):
    try:
        shutil.rmtree(path)
    except FileNotFoundError:
        pass

    try:
        os.mkdir(path)
    except FileExistsError:
        pass


def send_slack_webhook(new_vacancies_count, email):
    slack = Slack(url='https://hooks.slack.com/services/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')
    slack.post(text='За эту неделю появилось' + str(new_vacancies_count) + ' новых вакансий. Email: ' + email)


@app.task
def run_hhru_parser():
    create_dir('./data/vacancies/')
    create_dir('./data/employers_top/')

    for combination in set(search_combinations):
        vacancies_urls = []
        employers_statistic = {}
        new_vacancies_count = 0

        soup = get_soup(url + combination)

        last_page_block = soup.select('.bloko-button-group > span')[-1]
        last_page = int(last_page_block.select('a.bloko-button')[-1].text) - 1

        new_vacancies_count = get_vacancies(soup, vacancies_urls, new_vacancies_count)
        employers_statistic = get_employers_statistic(soup, employers_statistic)

        for i in range(1, last_page + 1):
            soup = get_soup(url + combination + '&page=' + str(i))
            new_vacancies_count = get_vacancies(soup, vacancies_urls, new_vacancies_count)
            employers_statistic = get_employers_statistic(soup, employers_statistic)

        csv_vacancies_data = [vacancy for vacancy in enumerate(vacancies_urls, 1)]
        write_data('./data/vacancies/' + combination + '.csv', csv_vacancies_data)

        sorted_employers_statistic = sorted(employers_statistic.items(), key=lambda x: x[1], reverse=True)
        write_data('./data/employers_top/' + combination + '.csv', sorted_employers_statistic)

        send_slack_webhook(new_vacancies_count, 'makov.sergey.it@gmail.com')


app.conf.beat_schedule = {
    'run_hhru_parser-task': {
        'task': 'hhru_parser.run_hhru_parser',
        'schedule': crontab(day_of_week='monday'),
    }
}
