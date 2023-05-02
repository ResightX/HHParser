from bs4 import BeautifulSoup
from dataclasses import dataclass
import urllib.request
import re
import json
from typing import List, Tuple

@dataclass
class Company:
    name: str
    has_awards: bool
    is_verified: bool
    is_accredited: bool
    rating: float
    review_count: int

@dataclass
class Vacancy:
    title: str
    wage: int
    company_name: str

def find_pages(soup: BeautifulSoup) -> int:
    pages = 0
    for item in soup.find_all('div'):
        for span in item.find_all('span'):
            try:
                if re.match('pager-page-wrapper.*', span.attrs['data-qa']):
                    pages = int(span.attrs['data-qa'].split('-')[-2])
            except:
                continue

    return pages

def parse_company_info(url: str) -> Tuple[float, int]:
    with urllib.request.urlopen(url) as fp:
        data = fp.read().decode('utf-8')
    soup = BeautifulSoup(data, 'html.parser')
    rating = "NULL"
    reviews = "NULL"

    for item in soup.find_all('div'):
        try:
            if item.attrs['class'][0] == 'EmployerReviewsFront-ReactRoot':
                for rat in item.find_all('div'):
                    try:
                        if rat.attrs['data-qa'] == 'employer-review-small-widget-total-rating':
                            rating = rat.string.replace(',', '.')
                    except:
                        continue
                for rev in item.find_all('span'):
                    try:
                        matches = re.match(r'[0-9,]*', str(rev).split('<!-- -->')[0].split('>')[1]).group()
                        if (',' not in matches) and matches != '':
                            reviews = int(matches)
                    except:
                        continue
        except:
            continue

    del soup

    return rating, reviews

def parse_page(soup: BeautifulSoup, company_names: List[str]) -> Tuple[List[Vacancy], List[Company]]:
    vacancies = []
    companies = []

    for item in soup.find_all('div', class_='serp-item'):
        tmpv = Vacancy(None, "NULL", None)
        tmpc = Company(None, 0, 0, 0, "NULL", "NULL")

        title = item.find('a', class_='serp-item__title')
        if title:
            tmpv.title = title.string

        wage = item.find('span', attrs={'data-qa': 'vacancy-serp__vacancy-compensation'})
        if wage:
            wagelist = [int(x) for x in re.sub(r"[^ [0-9]]*", "", ''.join(str(wage).split('>')[1:])).strip().split('  ')]
            tmpv.wage = sum(wagelist) // len(wagelist)

        verified = item.find('span', class_='vacancy-serp-bage-trusted-employer')
        if verified:
            tmpc.is_verified = 1

        awards = item.find('span', class_=re.compile(r'vacancy-serp-bage-hr.*'))
        if awards:
            tmpc.has_awards = 1

        accredited = item.find('span', class_=re.compile(r'it-accreditation.*'))
        if accredited:
            tmpc.is_accredited = 1

        company_name = item.find('a', attrs={'data-qa': 'vacancy-serp__vacancy-employer'})
        if company_name:
            tmpv.company_name = re.sub(r'[^ [a-zA-Zа-яА-Я0-9]]*', '', ''.join(str(company_name).split('</a>')[0].split('>')[1:]))
            if tmpv.company_name not in company_names:
                company_names.append(tmpv.company_name)
                tmpc.rating, tmpc.review_count = parse_company_info('https://hh.ru' + company_name.attrs['href'])
                tmpc.name = tmpv.company_name

        if tmpv.title is not None:
            vacancies.append(tmpv)
        if tmpc.name is not None:
            companies.append(tmpc)

    return vacancies, companies

def scrape() -> Tuple[List[Vacancy], List[Company]]:
    data = None
    pages = None
    page = 0
    vacancies = []
    companies = []
    company_names = []

    while True:
        with urllib.request.urlopen(f'https://vladimir.hh.ru/search/vacancy?no_magic=true&L_save_area=true&text=&excluded_text=&professional_role=156&professional_role=160&professional_role=10&professional_role=12&professional_role=150&professional_role=25&professional_role=165&professional_role=34&professional_role=36&professional_role=73&professional_role=155&professional_role=96&professional_role=164&professional_role=104&professional_role=157&professional_role=107&professional_role=112&professional_role=113&professional_role=148&professional_role=114&professional_role=116&professional_role=121&professional_role=124&professional_role=125&professional_role=126&area=23&salary=&currency_code=RUR&experience=doesNotMatter&order_by=relevance&search_period=0&items_on_page=20&page={page}') as fp: # Запрашиваемый URL-адрес динамически генерируется с помощью f-строки, при этом переменная page является заполнителем, который будет заменен на номер конкретной страницы при выполнении запроса. URL включает различные параметры поиска, такие как professional_role, area и items_on_page. URL можно скопировать из адресной строки браузера, после выставления всех необходимых настроек на сайте hh.ru; В качестве последнего параметра f-строки необходимо указать page={page}.
            data = fp.read().decode('utf-8')

        soup = BeautifulSoup(data, 'html.parser')

        if pages is None:
            pages = int(find_pages(soup))

        parsed_data = parse_page(soup, company_names)
        vacancies.extend(parsed_data[0])
        companies.extend(parsed_data[1])

        del soup
        print("Parsed: " + str(len(vacancies)))

        page += 1
        if page >= pages:
            break
    
    return vacancies, companies
