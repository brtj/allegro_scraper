# -*- coding: utf-8 -*-
import configparser
import urllib3
from urllib3 import ProxyManager, make_headers
from bs4 import BeautifulSoup
import re
import statistics
urllib3.disable_warnings()

def read_ini():
    config = configparser.ConfigParser()
    config.read_file(open(r'proxy_config.ini'))
    login = config.get('PROXY_CREDENTIALS', 'login')
    password = config.get('PROXY_CREDENTIALS', 'pass')
    return login, password
    
def get_data(www):
    http = urllib3.PoolManager()
    login, password = read_ini()
    proxy_credentials = ''.join(login + ':' + password)
    default_headers = make_headers(proxy_basic_auth=proxy_credentials)
    http = ProxyManager("http://gskproxy.gsk.com:800", proxy_headers=default_headers)
    r = http.request('GET', www)
    print('HTTP response: %s' % r.status)
    return r.data
    
def pages(www):
    html_doc = get_data(www)
    soup = BeautifulSoup(html_doc, 'html.parser')
    pages = soup.find_all('li', {'class': 'quantity'})[0].find('a').string
    print('Results in %s page/pages' % pages) #&p=2
    return pages

def get_links(www):
    page = int(pages(www))
    links_dict = []
    for x in range(page):
        page = x + 1
        page_param = '&p=' + str(page)
        url_full = www + page_param
        #print(url_full)
        html_doc = get_data(url_full)
        soup = BeautifulSoup(html_doc, 'html.parser')
        cars = soup.find_all('div', {'id': 'opbox-listing'})[0].find_all('article')
        print('Car/s on page: %s' % len(cars))
        for x in cars:
            test = x.find('a', href=True)
            links_dict.append(test['href'])
    print('Links gathered: %s' % len(links_dict))
    return links_dict

def parse_cars(www):
    cars_list = get_links(www)
    price_list = []
    mileage_list = []
    for x in cars_list:
        if 'otomoto.pl' in x:
            price, mileage = otomoto_pars(x)
            price_list.append(price)
            mileage_list.append(mileage)
        if 'allegro.pl' in x:
            print('ALLEGRO')
    #print(price_list)
    print('Median: %s PLN.' % statistics.median(price_list))
    print('Median low: %s PLN.' % statistics.median_low(price_list))
    print('Median high: %s PLN.' % statistics.median_high(price_list))
    print('Median grouped: %s PLN.' % statistics.median_grouped(price_list))
    print('Average price: %s PLN.' % statistics.mean(price_list))
    print('Most common price: %s PLN' % statistics.mode(price_list))
    print('Median: %s km.' % statistics.median(mileage_list))
    print('Median low: %s km.' % statistics.median_low(mileage_list))
    print('Median high: %s km.' % statistics.median_high(mileage_list))
    print('Median grouped: %s km.' % statistics.median_grouped(mileage_list))
    print('Average mileage: %s km.' % statistics.mean(mileage_list))
    print('Most common mileage: %s km' % statistics.mode(mileage_list))

def otomoto_pars(link):
    print('-----------------------------------------')
    html_doc = get_data(link)
    soup = BeautifulSoup(html_doc, 'html.parser')
    print(link)
    price = otomoto_price(soup)
    mileage = otomoto_mileage(soup)
    return price, mileage

    
def otomoto_price(soup):
    price_content = soup.find_all('div', {'class': 'offer-price'})[0]
    price_value = price_content.find_all('span', {'class': 'offer-price__number'})[0].text
    price = ''.join(re.findall('\d+', price_value))
    print('Price: %s PLN.' % price)
    return int(price)
    
def otomoto_mileage(soup):
    mileage_content = soup.find_all('div', {'class': 'offer-header__row'})[0]
    mileage_value = mileage_content.find_all('span', {'class': 'offer-main-params__item'})[1].text
    mileage = ''.join(re.findall('\d+', mileage_value))
    print('Mileage: %s km.' % mileage)
    return int(mileage)
        
car_url = 'https://allegro.pl/kategoria/alfa-romeo-mito-57960?order=m&rodzaj-paliwa=Benzyna'
parse_cars(car_url)

# https://allegro.pl/kategoria/alfa-romeo-mito-57960?order=m&rodzaj-paliwa=Benzyna
# https://allegro.pl/kategoria/alfa-romeo-4c-249623?order=m