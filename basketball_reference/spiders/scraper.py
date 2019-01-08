from bs4 import BeautifulSoup

import requests

def make_soup(url):
  url_request = requests.get(url)
  html = url_request.text
  soup = BeautifulSoup(html, 'html.parser')
  return soup

def store_html(name, url):
  url_request = requests.get(url)
  html = url_request.text
  f = open("{}.html".format(name), "w+")
  f.write(html)
  f.close()

def get_soup(name):
  f = open("{}.html".format(name), "r")
  html = f.read()
  f.close()
  soup = BeautifulSoup(html, 'html.parser')
  return soup
