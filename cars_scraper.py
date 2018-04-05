# -*- coding: utf-8 -*-
import configparser
import urllib3
from urllib3 import ProxyManager, make_headers
from bs4 import BeautifulSoup
import re
import statistics
from time import strftime, localtime
import io
urllib3.disable_warnings()

def read_ini():
    config = configparser.ConfigParser()
    config.read_file(open(r'proxy_config.ini'))
    login = config.get('PROXY_CREDENTIALS', 'login')
    password = config.get('PROXY_CREDENTIALS', 'pass')
    return login, password
    
def get_data(www):
    http = urllib3.PoolManager()
    retries = urllib3.util.Retry(read=3, backoff_factor=5,
            status_forcelist = frozenset([500,501,502,503,504,429]))
    http = urllib3.PoolManager(retries=retries)
    login, password = read_ini()
    proxy_credentials = ''.join(login + ':' + password)
    default_headers = make_headers(proxy_basic_auth=proxy_credentials)
    #http = ProxyManager("http://gskproxy.gsk.com:800", proxy_headers=default_headers)
    r = http.request_encode_url('GET', www)
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
        print('Car/s on page: %s, page number: %s' % (len(cars), page))
        for x in cars:
            test = x.find('a', href=True)
            links_dict.append(test['href'])
    print('Links gathered: %s' % len(links_dict))
    return links_dict

def parse_cars(www):
    start_time = gettime()
    print('Script started at: %s' % start_time)
    cars_list = get_links(www)
    price_list = []
    mileage_list = []
    year_list = []
    fuel_type = []
    seller_type = []
    seller_nickname = []
    seller_address = []
    counter = 0
    counter_otom = 0
    counter_alle = 0
    print('-----------------------------------------')
    for x in cars_list:
        counter += 1
        print('Car %s of %s' % (counter, len(cars_list)))
        if 'otomoto.pl' in x:
            counter_otom += 1
            price, mileage, year, seller, nickname, address, fuel = otomoto_pars(x)
            price_list.append(price)
            mileage_list.append(mileage)
            year_list.append(year)
            seller_type.append(seller)
            seller_nickname.append(nickname)
            seller_address.append(address)
            fuel_type.append(fuel)
            print('-----------------------------------------')
        if 'allegro.pl' in x:
            counter_alle += 1
            print('ALLEGRO')
            print('-----------------------------------------')
    #print(year_list)
    print('Based on %s cars' % len(cars_list))
    print('%s cars from otomoto.pl' % counter_otom)
    print('%s cars from allegro.pl' % counter_alle)
    print('Script started at %s and finished at %s' % (str(start_time), gettime()))
    print('Min price: %s PLN' % min(price_list))
    print('Max price: %s PLN' % max(price_list))
    print('Median: %s PLN' % statistics.median(price_list))
    print('Median low: %s PLN' % statistics.median_low(price_list))
    print('Median high: %s PLN' % statistics.median_high(price_list))
    print('Median grouped: %s PLN' % round(statistics.median_grouped(price_list),1))
    print('Average price: %s PLN' % round(statistics.mean(price_list),1))
    print('Min mileage: %s km' % min(mileage_list))
    print('Max mileage: %s km' % max(mileage_list))
    print('Median: %s km' % statistics.median(mileage_list))
    print('Median low: %s km' % statistics.median_low(mileage_list))
    print('Median high: %s km' % statistics.median_high(mileage_list))
    print('Median grouped: %s km' % statistics.median_grouped(mileage_list))
    print('Average mileage: %s km' % round(statistics.mean(mileage_list),1))
    print('Oldest car from %s year' % min(year_list))
    print('Newest car from %s year' % max(year_list))
    print('Median: %s year' % statistics.median(year_list))
    print('Median low: %s year' % statistics.median_low(year_list))
    print('Median high: %s year' % statistics.median_high(year_list))
    print('Median grouped: %s year' % round(statistics.median_grouped(year_list),0))
    print('Average year: %s' % round(statistics.mean(year_list),1))
    create_csv_file(www, cars_list, price_list, mileage_list, year_list,
                    seller_type, seller_nickname, seller_address, fuel_type)

def otomoto_pars(link):
    html_doc = get_data(link)
    soup = BeautifulSoup(html_doc, 'html.parser')
    print(link)
    price = otomoto_price(soup)
    mileage = otomoto_mileage(soup)
    year = otomoto_year(soup)
    seller, nickname, address = otomoto_seller(soup)
    fuel_type = otomoto_fuel_type(soup)
    #description = otomoto_description(soup)
    return price, mileage, year, seller, nickname, address, fuel_type
    
def otomoto_price(soup):
    price_content = soup.find_all('div', {'class': 'offer-price'})[0]
    price_value = price_content.find_all('span', {'class': 'offer-price__number'})[0].text
    price = ''.join(re.findall('\d+', price_value))
    print('Price: %s PLN' % price)
    return int(price)
    
def otomoto_mileage(soup):
    mileage_content = soup.find_all('div', {'class': 'offer-header__row'})[0]
    mileage_value = mileage_content.find_all('span', {'class': 'offer-main-params__item'})[1].text
    mileage = ''.join(re.findall('\d+', mileage_value))
    print('Mileage: %s km' % mileage)
    if mileage is '':
        mileage = 0
    return int(mileage)

def otomoto_year(soup):
    year_content = soup.find_all('div', {'class': 'offer-header__row'})[0]
    year_value = year_content.find_all('span', {'class': 'offer-main-params__item'})[0].text
    year = ''.join(re.findall('\d+', year_value))
    print('Year: %s' % year)
    return int(year)

def otomoto_fuel_type(soup):
    fuel_type_content = soup.find_all('div', {'class': 'offer-header__row'})[0]
    fuel_type_value = fuel_type_content.find_all('span', {'class': 'offer-main-params__item'})[2].text
    fuel_type = fuel_type_value.strip()
    print('Fuel type: %s' % fuel_type)
    return fuel_type

def otomoto_seller(soup):
    seller_content = soup.find_all('div', {'class': 'seller-box__seller-info'})[0]
    seller_type = seller_content.find_all('small', {'class': 'seller-box__seller-type'})[0].text
    seller_address_content = soup.find_all('div', {'class': 'seller-box__seller-address'})[0]
    seller_address = seller_address_content.find_all('span', {'class': 'seller-box__seller-address__label'})[0]
    seller_nickname = seller_content.find_all('h2', {'class': 'seller-box__seller-name'})[0]
    seller_nickname = seller_nickname.text.strip()
    seller_address = seller_address.text.strip()
    print('Seller type: %s' % seller_type)
    print('Seller nickname: %s' % seller_nickname)
    print('Address: %s' % seller_address)
    return seller_type, seller_nickname, seller_address

def otomoto_description(soup):
    description_content = soup.find_all('div', {'class': 'offer-description'})[0]
    description = description_content.find_all('div')[0]
    print('Description: %s' % description.text.strip()[:20])
    
def gettime():
    time_str = strftime('%Y-%m-%d %H:%M:%S', localtime())
    return time_str
    
def create_csv_file(www, link, price, mileage, year, seller_t, seller_n, seller_a, fuel_type):
    filename = file_name(www)
    f_csv = io.open(filename + '.csv','w',encoding='utf-8-sig', errors='ignore')
    csv_header_line = '"num","link","fuel type","price","mileage","year","seller_type","seller_nickname","seller_address'
    f_csv.write(csv_header_line + '\n')
    for x in range(len(price)):
        csv_line = ('"' + str(x) + '","' + link[x] + '","' + str(fuel_type[x]) +
            '","' + str(price[x]) + '","' + str(mileage[x]) + '","' + str(year[x]) +
            '","' + str(seller_t[x]) + '","' + str(seller_n[x]) +
            '","' + str(seller_a[x]) + '"\n')
        f_csv.write(csv_line)
    f_csv.close()
    print('CSV file generated: %s.csv' % filename)
    
def file_name(link):
    f_allegro = re.search("allegro.pl", link)
    file_name_se = (link[f_allegro.start():])
    f_que_mark = file_name_se.rfind('?')
    file_name = file_name_se[:f_que_mark]
    f_last = file_name.rfind('-')
    file_name = (file_name_se[:f_last])[21:].replace('-','_')
    date = strftime('%Y_%m_%d_%H_%M_%S', localtime())
    full_name = file_name + '_' + date + '_export'
    return full_name

def car_url_build(car_url):
    crashed = 'Nie'
    fuel_type = 'Diesel' #Benzyna #Diesel
    crashed_label = '&uszkodzony='
    fuel_type_label = '&rodzaj-paliwa='
    full_url = ''.join(car_url + crashed_label + crashed + fuel_type_label + fuel_type)
    print(full_url)
    return full_url

car_url = 'https://allegro.pl/kategoria/passat-b6-2005-2010-12764?order=m'
parse_cars(car_url_build(car_url))


# https://allegro.pl/kategoria/alfa-romeo-159-18050?order=m
# https://allegro.pl/kategoria/alfa-romeo-159-18050?order=m
# https://allegro.pl/kategoria/alfa-romeo-mito-57960?order=m
# https://allegro.pl/kategoria/alfa-romeo-4c-249623?order=m
# https://allegro.pl/kategoria/alfa-romeo-spider-27879?order=m