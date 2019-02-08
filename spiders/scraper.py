from bs4 import BeautifulSoup
from requests_html import HTMLSession
import random
import time

LONG_ABBREV_DICT = {
  "Atlanta": "ATL",
  "Boston": "BOS",
  "Brooklyn": "BRK",
  "Chicago": "CHI",
  "Charlotte": "CHO",
  "Cleveland": "CLE",
  "Dallas": "DAL",
  "Denver": "DEN",
  "Detroit": "DET",
  "Golden State": "GSW",
  "Houston": "HOU",
  "Indiana": "IND",
  "LA Clippers": "LAC",
  "LA Lakers": "LAL",
  "Memphis": "MEM",
  "Miami": "MIA",
  "Milwaukee": "MIL",
  "Minnesota": "MIN",
  "New Orleans": "NOP",
  "New York": "NYK",
  "Oklahoma City": "OKC",
  "Orlando": "ORL",
  "Philadelphia": "PHI",
  "Phoenix": "PHO",
  "Portland": "POR",
  "Sacramento": "SAC",
  "San Antonio": "SAS",
  "Toronto": "TOR",
  "Utah": "UTA",
  "Washington": "WAS"
}

def get_soup(url, render=False):
  session = HTMLSession()
  response = session.get(url,timeout=5)
  if response.status_code != 200:
    return None
  if render:
    response.render()
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
  elif value == "—":
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