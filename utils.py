# utils.py
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import csv
from driver_setup import random_delay

def generate_date_strings(start_date, end_date):
    start = datetime.strptime(start_date, '%Y/%m/%d')
    end = datetime.strptime(end_date, '%Y/%m/%d')
    
    date_strings = set()
    current = start
    while current <= end:
        date_strings.add(current.strftime('%Y%m'))
        next_month = current.replace(day=28) + timedelta(days=4)
        current = next_month.replace(day=1)
    
    return sorted(date_strings)

def get_soup(driver, url):
    driver.get(url)
    random_delay(3, 5)
    html = driver.page_source
    return BeautifulSoup(html, 'lxml')

def save_racedata_to_csv(dataflame, csv_file_path):
    with open(csv_file_path, mode='w', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)
        for race in  dataflame.itertuples(index=False):
            print(race)
            print("\nType of race:", type(race))
            writer.writerow(race)