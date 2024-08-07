'''Utility functions scraping web pages'''

# import asyncio, httpx
import requests
import shutil
import time
from bs4 import BeautifulSoup
# from dotenv import dotenv_values
# from markdownify import markdownify as md

# async def get_page_soup_async(url: str) -> BeautifulSoup:
#     '''Returns BeautifulSoup for a web page'''
#     r = httpx.get(url)
#     encoding = r.encoding if 'charset' in r.headers.get('content-type', '').lower() else None
#     parser = 'html.parser'
#     soup = BeautifulSoup(r.content, parser, from_encoding=encoding)
#     return soup


def get_page_soup(url: str) -> BeautifulSoup:
    '''Returns BeautifulSoup for a web page'''
    r = requests.get(url)
    encoding = r.encoding if 'charset' in r.headers.get('content-type', '').lower() else None
    parser = 'html.parser'
    soup = BeautifulSoup(r.content, parser, from_encoding=encoding)
    return soup

def get_html_from_soup(soup: BeautifulSoup, selector: str) -> list:
    '''Returns a list of HTML tags given a particular CSS selector pattern'''
    html = soup.select(selector)
    return html

def get_text_from_soup(soup: BeautifulSoup, selector: str) -> str:
    '''Returns a text string, given a particular CSS selector pattern'''
    html = soup.select(selector)
    if len(html) > 0:
        return html[0].get_text()

def get_multi_text_from_soup(soup: BeautifulSoup, selector: str) -> list:
    '''Returns a text string, given a particular CSS selector pattern'''
    html = soup.select(selector)
    html_set = []
    for row in html:
        html_set.append(row.get_text().strip())
    return html_set

def get_attrib_value_from_soup(soup: BeautifulSoup, selector: str, attribute: str) -> str:
    '''Returns a string for a particular HTML attribute'''
    # if dom.xpath(xpath):
    if soup.select(selector):
        attribute_value = soup.select_one(selector)[attribute]
        return attribute_value.strip()

def get_nested_fields(dom: str, nested_fields_xpath: dict) -> str:
    '''Returns nested fields from the dom, in original order'''

    # TODO Make a table of actual_nest_fields / values
    nested_fields_values = dom.xpath(nested_fields_xpath.values)
    nested_fields = []

    # Match Dato-fieldnames (keys)
    for value in nested_fields_values:
        for key, val in nested_fields_xpath.items():
            if value == val:
                nested_field = key
                nested_fields.append(nested_field)

    content = zip(nested_fields, nested_fields_values)

    # TODO: For each nested_field, add rest of required dato-model-fields

    return content


def get_image(url:str=None, local_path:str=None):
    '''downloads an image file from a given image-url - from https://stackoverflow.com/a/18043472'''

    response = requests.get(url, stream=True)    

    time.sleep(.5)

    with open(local_path, 'wb') as out_file:
        shutil.copyfileobj(response.raw, out_file)

    del response

