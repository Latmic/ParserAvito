import csv
import sys
from pathlib import Path
from typing import NamedTuple

from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement

RESULT_FILENAME = Path('ads.csv')
AD_CSS_SELECTOR ='div[data-marker="item"]'


class Ad(NamedTuple):
    id: str
    title: str
    price: int
    link: str


def get_category_url():
    return sys.argv[1]


def does_page_contain_ads(driver: webdriver.Chrome) -> bool:
    return len(driver.find_elements_by_css_selector(AD_CSS_SELECTOR)) > 0


def parse_category(category_url: str) -> list[Ad]:
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = webdriver.Chrome(executable_path='./chromedriver', options=options)

    ads = []
    page_number = 1
    url_template = category_url + '&p={}'

    driver.get(url_template.format(page_number))

    while does_page_contain_ads(driver):
        page_ads = parse_page(driver)
        ads.extend(page_ads)

        page_number += 1
        driver.get(url_template.format(page_number))

    return ads


def parse_page(driver: webdriver.Chrome) -> list[Ad]:
    ad_elements = driver.find_elements_by_css_selector(AD_CSS_SELECTOR)
    return [parse_ad(ad_element) for ad_element in ad_elements]


def parse_ad(element: WebElement) -> Ad:
    return Ad(
        id=element.get_attribute('id'),
        title=element.find_element_by_css_selector('h3').text,
        price=element.find_element_by_css_selector('meta[itemprop="price"]').get_attribute('content'),
        link=element.find_element_by_css_selector('a[data-marker="item-title"]').get_attribute('href')
    )


def save_ads(ads: list[Ad]):
    fieldnames = ['id', 'title', 'price', 'link']
    need_to_write_header = False

    if not RESULT_FILENAME.exists():
        need_to_write_header = True
        RESULT_FILENAME.touch()

    with RESULT_FILENAME.open() as f:
        existing_ids = {row['id'] for row in csv.DictReader(f)}

    with RESULT_FILENAME.open(mode='a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        if need_to_write_header:
            writer.writeheader()

        writer.writerows([ad._asdict() for ad in ads if ad.id not in existing_ids])


# https://www.avito.ru/kostroma/noutbuki?f=ASgCAQICAUDwvA0UiNI0&user=1

if __name__ == '__main__':
    category_url = get_category_url()
    ads = parse_category(category_url)
    save_ads(ads)
