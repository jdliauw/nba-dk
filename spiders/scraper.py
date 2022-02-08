from bs4 import BeautifulSoup
from requests_html import HTMLSession
import random
import time


def get_soup(url, render=False):
  session = HTMLSession()
  sleep(3,5)
  response = session.get(url,timeout=5)
  if response.status_code != 200:
    return None
  if render:
    response.html.render()
  soup = BeautifulSoup(response.text, "html.parser")
  return soup

def get_number_type(value):
  try:
    value = int(value)
  except ValueError:
    try:
      value = float(value)
    except ValueError:
      # string
      if len(value) > 0:
        return value
      else: 
        return 0.0
  return value

def get_converted_type(value):
  if "." in value:
    value = float(value)
  elif value == "-":
    value = 0.0
  else:
    try:
      value = int(value)
    except:
      if not isinstance(value, str):
        print("WTF DUDE WHAT TYPE IS ME")
  return value

# robots.txt asks for 3s
def sleep(min_time, max_time):
  time.sleep(random.randint(min_time, max_time) + random.randint(1,100)/100)