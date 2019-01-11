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
  response = session.get(url)
  if render:
    response.render()
  soup = BeautifulSoup(response.text, "html.parser")
  return soup

# robots.txt asks for 3s
def sleep():
  time.sleep(random.randint(3,8) + random.randint(1,100)/100)