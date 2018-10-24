import os
import threading
import django
import requests
import datetime
from django.utils import timezone
import pytz
from bs4 import BeautifulSoup

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nparse.settings")
django.setup()
from main_app.models import *


class Nparse:
    """main class to run parser and save information to DB"""
    PREF = "https://www.nasdaq.com/symbol/"
    POST_HIST = "/historical/"
    POST_INST = "/insider-trades"
    HIST_ROWS = 6
    INS_ROWS = 8

    def __init__(self, n=3):
        self.n = n
        self.pool = {}

    @staticmethod
    def init_companies(filename="tickers.txt"):
        '''
        open filename and save company ticker in database
        :param filename: path to filename with tickers
        :return:
        '''
        Company.objects.all().delete()
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                company = Company(slug=line.replace('\r', '').replace('\n', ''))
                company.save()

    @staticmethod
    def get_content(url):
        '''
        download html page from url
        :param url: https://www.example.com
        :return: html page
        '''
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
        html_page = requests.get(url, {'User-Agent': headers}).text
        return html_page

    def parse_price(self, task_num,  task_list):
        '''
        download prices and write them to database
        :param task_num: number of thread, not used yet
        :param task_list: list of tickers, parsed in current thread
        :return:
        '''
        HistoryRecord.objects.all().delete()
        for company in task_list:
            # url = https://www.nasdaq.com/symbol/<ticker>/historical
            url = "".join([self.PREF, company.slug, self.POST_HIST])
            soup = BeautifulSoup(self.get_content(url), 'html.parser')
            tdata = soup.find(id="historicalContainer").find_all('td')
            for item in self.get_table_rows(tdata, self.HIST_ROWS):
                ts = dict({
                    'company': company,
                    'open': item[1].replace(',', ''),
                    'high': item[2].replace(',', ''),
                    'low': item[3].replace(',', ''),
                    'close': item[4].replace(',', ''),
                    'volume': item[5].replace(',', ''),
                })
                try:
                    ts['date'] = datetime.datetime.strptime(item[0], '%m/%d/%Y')

                except ValueError:
                    ts['date'] = timezone.now()
                rec = HistoryRecord(**ts)
                rec.save()

    @staticmethod
    def get_table_rows(tdata, col):
        """
        return generator of where one return value correspond to table row
        :param tdata: table data
        :param col: number of columns in table
        :return:
        """
        for i in range(0, len(tdata), col):
            yield [''.join(x.text.split()) for x in tdata[i: i+col]]

    def parse_insiders(self, task_num, task_list):
        '''
        parse insiders data
        :param task_num: number of current thread, do not used yet
        :param task_list: list of tickets to parse
        :return:
        '''
        InsiderRecord.objects.all().delete()
        for company in task_list:
            # url = https://www.nasdaq.com/symbol/<ticker>/insider-trades
            url = "".join([self.PREF, company.slug, self.POST_INST])
            # print(url)
            soup = BeautifulSoup(self.get_content(url), 'html.parser')
            paginator = soup.find_all("a", {"class": "pagerlink"})
            self.disassemble_insider_page(company, soup)
            pages = []
            for page in paginator:
                try:
                    pages.append(int(page.text))
                except ValueError:
                    continue
            try:
                max_page = max(pages)
                if max_page > 10:
                    max_page = 10
                additional_links = []
            except ValueError:
                max_page = 0
            if max_page:
                for i in range(2, max_page+1):
                    additional_links.append("".join([url.lower(), '?page={}'.format(i)]))
                print(additional_links)

    def disassemble_insider_page(self, company, soup):
        tdata = soup.find("div", {"class": "genTable"}).find_all('td')
        print(tdata)

    def run_parse_history(self):
        """
        run in n threads pool of jobs
        :return:
        """
        self.pool = self.create_pool()
        for task_num, task_list in self.pool.items():
            task = threading.Thread(target=self.parse_price, args=(task_num, task_list,))
            task.start()

    def run_parse_insiders(self):
        self.pool = self.create_pool()
        for task_num, task_list in self.pool.items():
            task = threading.Thread(target=self.parse_insiders, args=(task_num, task_list,))
            task.start()

    def create_pool(self):
        '''
        create dict where key is number of thread according to
        self.n, and value is list of companies, which we want to parse
        in this specific thread
        :return:
        '''
        companies = Company.objects.all()
        pool = dict((key, list()) for key in range(self.n))
        key = 0
        for item in companies:
            pool[key].append(item)
            key += 1
            if key >= self.n:
                key = 0
        return pool


if __name__ == '__main__':
    p = Nparse(n=3)
    # p.init_companies('tickers.txt')
    # p.run_parse_history()
    # p.run_parse_insiders()
