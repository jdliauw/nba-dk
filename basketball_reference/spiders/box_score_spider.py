from bs4 import BeautifulSoup
from datetime import datetime, date, timedelta

import logging
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
    # print(stats)

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
      # basketball-reference columns
      for i, v in enumerate(["time", "home_play", "home_points", "score", "away_points", "away_play"]):
        if i in [2, 4]:
          continue

        td_text = tds[i].text

        # PLAYS
        # basketball-reference divides plays by home/away, but for our purposes we don't care since 
        # we can extract this from the player. as far as i know, there is no instance where there is 
        # both a home and away play, but we'll throw an exception in case
        if i in [1, 5] and len(td_text) > 1:
          parse_play(tds[i], stat)
        elif len(td_text) > 1:
          stat[v] = td_text
    elif tds_size == 2:
      stat["time"] = tds[0].text
      stat["play"] = tds[1].text
      # print(stat["play"])
    
    if stat:
      stats.append(stat)

  # for stat in stats:
    # if len(stat) > 2:
      # print(stat)

def parse_play(td, stat):
  td_text = td.text
  # example: J. Simmons makes 3-pt jump shot from 25 ft (assist by D. Augustin)
  if " makes " in td_text:
    # add scorer/assister
    a_tags = td.findAll("a")
    if len(a_tags) == 2:
      # extract the href from the tag, then parse the url to get the playerid 
      # example: <a href="/players/a/augusdj01.html">D. Augustin</a>
      stat["scorer"] = a_tags[0]["href"].split("/")[-1][:-5]
      stat["assister"] = a_tags[1]["href"].split("/")[-1][:-5]
    elif len(a_tags) == 1:
      stat["scorer"] = a_tags[0]["href"].split("/")[-1][:-5]
      stat["type"] = 1
    else:
      logging.warning("WTF, NOT THE RIGHT AMOUNT OF A TAGS IN SCORER/ASSISTER PARSING")

    if "-pt" in td_text:
      stat["type"] = int(td_text[td_text.find("-pt")-1 : td_text.find("-pt")])
      
      key_offset = [("jump shot from ", 15),
                    ("hook shot from ", 15),
                    ("layup from ", 11),
                    ("dunk from ", 10),
                    ]
      for type, offset in key_offset:
        if type in td_text:
          stat["distance"] = int(td_text[td_text.find(type) + offset : td_text.find(" ft")]) 

      key_offset = [("layup at", 9),
                    ("dunk at", 8),
                    ]
      for type, offset in key_offset:
        if type in td_text:
          stat["distance"] = 0
  if " misses " in td_text:
    print(td_text)

def main():
  logging.basicConfig(filename='pbp.log',level=logging.DEBUG)

  yesterday = date.today() - timedelta(1)
  # scrape_box_scores(yesterday.month, yesterday.day, yesterday.year)
  scrape_pbp("https://www.basketball-reference.com/boxscores/pbp/201812040MIA.html")


if __name__ == '__main__':
  main()

  # store and fetch from instead of requesting
  # store_html("insert url")
  # get_soup()