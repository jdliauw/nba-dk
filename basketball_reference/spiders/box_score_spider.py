from bs4 import BeautifulSoup
from datetime import datetime, date, timedelta

import random
import requests
import time

"""
hey this was cool: 
# if all(key in stat for key in ["time", "home_play"]):
"""

def make_soup(url):
  url_request = requests.get(url)
  html = url_request.text
  soup = BeautifulSoup(html, 'html.parser')
  return soup

def store_html(url):
  url_request = requests.get(url)
  html = url_request.text
  f = open("soup.html", "w+")
  f.write(html)
  f.close()

def get_soup():
  f = open("soup.html", "r")
  html = f.read()
  f.close()
  soup = BeautifulSoup(html, 'html.parser')
  return soup

def scrape_box_scores(month, day, year):
  url = "https://www.basketball-reference.com/boxscores/?month={}&day={}&year={}".format(month, day, year)
  soup = make_soup(url)
  a_tags = soup.find("div", {"class": "game_summaries"}).findAll("a")
  for a_tag in a_tags:
    href = a_tag["href"]
    if "boxscore" in href and a_tag.text == 'Box Score':
      base = "https://www.basketball-reference.com"
      # scrape_box_score(base + href)
      scrape_pbp(base + "/boxscores/pbp/" + href.split("/")[-1])

def scrape_box_score(box_score_url):
  # [3,6) second crawl delay; robots.txt asks for 3s
  time.sleep(4 + (10 * random.random() % 3))

  soup = make_soup(box_score_url)
  game_date = soup.find("div", {"class": "scorebox_meta"}).find("div").text
  datetime_object = datetime.strptime(game_date, "%I:%M %p, %B %d, %Y")
  year = int(datetime.strftime(datetime_object, "%Y"))
  month = int(datetime.strftime(datetime_object, "%m"))
  day = int(datetime.strftime(datetime_object, "%d"))
  weekday = datetime.strftime(datetime_object, "%A")

  tables = soup.findAll("table", {"class": ["sortable", "stats_table", "now_sortable"]})
  for table in tables:
    tbody = table.find("tbody")
    trs = tbody.findAll("tr")

    stats = []
    for i, tr in enumerate(trs):
      tds = tr.findAll("td")
      try:
        id = tr.th.a["href"].split("/")[-1][:-5]
        starter = True if i < 5 else False
        player = {"id": id, "starter": starter}

        for td in tds:
          player[td["data-stat"]] = td.text
        stats.append(player)
      except TypeError:
        pass
      except Exception as e:
        print(e)
    print(stats)

def scrape_pbp(pbp_url):
  # soup = make_soup(pbp_url)
  soup = get_soup()
  trs = soup.find("table", {"id": "pbp"}).findAll("tr")
  stats = []

  for tr in trs:
    tds = tr.findAll("td")
    tds_size = len(tds)
    stat = {}

    if tds_size == 6:
      for i, v in enumerate(["time", "home_play", "home_points", "score", "away_points", "away_play"]):

        # if i in [1, 5]:
          # stat["play"] = 

        td_text = tds[i].text
        if len(td_text) > 1 and v is "home_play":
          stat["home_play"] = td_text
        elif len(td_text) > 1 and v is "away_play":
          stat["away_play"] = td_text
        elif len(td_text) > 1:
          stat[v] = td_text
    elif tds_size == 2:
      stat["time"] = tds[0].text
      stat["home_play"] = tds[1].text
      stat["away_play"] = tds[1].text
    
    if stat:
      stats.append(stat)

  for stat in stats:
    if "home_play" in stat and "make" in stat["home_play"]:
      print(stat["home_play"])

if __name__ == '__main__':
  yesterday = date.today() - timedelta(1)
  # scrape_box_scores(yesterday.month, yesterday.day, yesterday.year)
  scrape_pbp("https://www.basketball-reference.com/boxscores/pbp/201812040MIA.html")

  # store and fetch from instead of requesting
  # store_html("insert url")
  # get_soup()