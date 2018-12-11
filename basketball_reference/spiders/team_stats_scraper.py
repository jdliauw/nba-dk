from bs4 import BeautifulSoup
from datetime import datetime, date, timedelta

import logging
import pdb
import random
import requests
import time

long_abbrev_dict = {
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

def scrape_day(month, day, year):
  url = "https://www.basketball-reference.com/boxscores/?month={}&day={}&year={}".format(month, day, year)
  soup = make_soup(url)
  a_tags = soup.find("div", {"class": "game_summaries"}).findAll("a")
  for a_tag in a_tags:
    href = a_tag["href"]
    if "boxscore" in href and a_tag.text == 'Box Score':
      base = "https://www.basketball-reference.com"
      scrape_box_score(base + href)
      scrape_pbp(base + "/boxscores/pbp/" + href.split("/")[-1])

def scrape_box_score(box_score_url):
  # [3,6) second crawl delay; robots.txt asks for 3s
  # time.sleep(4 + (10 * random.random() % 3))

  # soup = make_soup(box_score_url)
  soup = get_soup()
  game_date = soup.find("div", {"class": "scorebox_meta"}).find("div").text
  datetime_object = datetime.strptime(game_date, "%I:%M %p, %B %d, %Y")
  year = int(datetime.strftime(datetime_object, "%Y"))
  month = int(datetime.strftime(datetime_object, "%m"))
  day = int(datetime.strftime(datetime_object, "%d"))
  weekday = datetime.strftime(datetime_object, "%A")
  stats = {}
  
  tables = soup.findAll("table", {"class": ["sortable", "stats_table", "now_sortable"]})
  for table in tables:
    tbody = table.find("tbody")
    trs = tbody.findAll("tr")

    count = 0
    for i, tr in enumerate(trs):
      tds = tr.findAll("td")
      try:
        id = tr.th.a["href"].split("/")[-1][:-5]
        starter = True if i < 5 else False

        if id not in stats:
          stats[id] = {}
        stats[id]["starter"] = starter

        for td in tds:
          stats[id][td["data-stat"]] = td.text

      except TypeError:
        pass
      except Exception as e:
        logging.error("Exception {} caught".format(e))

  # TODO: store to database
  # for stat in stats:
  #   print(stat) 

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

    if stat:
      stats.append(stat)
  
  # TODO: store to database
  # for stat in stats:
  #   print(stat)

def parse_play(td, stat):
  td_text = td.text

  # MAKES/MISSES
  if any(k in td_text for k in [" makes ", " misses "]):
    # make or miss
    if " makes " in td_text:
      stat["make"] = True
    else:
      stat["make"] = False

    a_tags = td.findAll("a")
    if len(a_tags) == 2:
      # extract the href from the tag, then parse the url to get the playerid 
      # example: <a href="/players/a/augusdj01.html">D. Augustin</a>
      stat["scorer"] = a_tags[0]["href"].split("/")[-1][:-5]
      if " makes " in td_text:
        stat["assister"] = a_tags[1]["href"].split("/")[-1][:-5]
      elif " misses " in td_text:
        stat["blocker"] = a_tags[1]["href"].split("/")[-1][:-5]
      else:
        logging.warning("Unknown stat: {}".format(td_text))
    elif len(a_tags) == 1:
      stat["scorer"] = a_tags[0]["href"].split("/")[-1][:-5]
      stat["type"] = 1
    else:
      logging.warning("Unknown type of play: {}".format(td_text))

    # free throws are points scored but do not have "-pt"
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

  # REBOUNDS
  elif " rebound " in td_text:
    a_tags = td.findAll("a")
    if len(a_tags) == 1:
      if "offensive" in td_text.lower():
        stat["orebounder"] = a_tags[0]["href"].split("/")[-1][:-5]
      elif "defensive" in td_text.lower():
        stat["drebounder"] = a_tags[0]["href"].split("/")[-1][:-5]
      else:
        logging.warning("Unknown rebound type: {}".format(td_text))
    elif len(a_tags) == 0:
      if "offensive" in td_text.lower():
        stat["orebounder"] = "team"
      elif "defensive" in td_text.lower():
        stat["drebounder"] = "team"
    else:
      logging.warning("a_tags len of {}", len)

  # TIMEOUT (starting 2018 season, only full)
  elif " timeout" in td_text:
    team = td_text[:td_text.find(" full timeout")]
    stat["full_timeout"] = long_abbrev_dict[team]

  # TURNOVERS
  elif "Turnover " in td_text:
    a_tags = td.findAll("a")
    if len(a_tags) == 2:
      stat["turnover"] = a_tags[0]["href"].split("/")[-1][:-5]
      stat["steal"] = a_tags[1]["href"].split("/")[-1][:-5]
      stat["turnover_type"] = td_text[td_text.find("(") + 1: td_text.find(";")]
    elif len(a_tags) == 1:
      stat["turnover"] = a_tags[0]["href"].split("/")[-1][:-5]
      stat["turnover_type"] = td_text[td_text.find("(") + 1 : td_text.find(")")]
    elif len(a_tags) == 0:
      stat["turnover"] = "team"
      stat["turnover_type"] = td_text[td_text.find("(") + 1 : td_text.find(")")]
    else:
      logging.warning("Unknown type of turnover: {}".format(td_text))

  # FOULS
  elif any(k in td_text for k in ["Loose ball", "Personal foul", "Shooting foul", "Offensive foul", "Technical foul"]):
    a_tags = td.findAll("a")
    if len(a_tags) == 2:
      stat["fouler"] = a_tags[0]["href"].split("/")[-1][:-5]
      stat["foul_drawer"] = a_tags[1]["href"].split("/")[-1][:-5]

      if "Loose ball" in td_text:
        stat["foul_type"] = "loose ball"
      elif "Personal foul" in td_text:
        stat["foul_type"] = "personal"
      elif "Shooting foul" in td_text:
        stat["foul_type"] = "shooting"
      elif "Offensive foul" in td_text:
        stat["foul_type"] = "offensive"
      else:
        logging.warning("Unknown type of foul: {}".format(td_text))  
    elif len(a_tags) == 1 and "Technical foul" in td_text:
      stat["fouler"] = a_tags[0]["href"].split("/")[-1][:-5]
      stat["foul_type"] = "technical"
    else:
      logging.warning("Unknown type of foul: {}".format(td_text))

  elif "enters the game" in td_text:
    a_tags = td.findAll("a")
    if len(a_tags) == 2:
      stat["sub_in"] = a_tags[0]["href"].split("/")[-1][:-5]
      stat["sub_out"] = a_tags[1]["href"].split("/")[-1][:-5]
    else:
      logging.warning("Unknown type of substitution: {}".format(td_text))

  elif "Violation " in td_text:
    stat["team_violation"] = "kicked ball"

  else:
    logging.warning("Unknown type of play: {}".format(td_text))

def main():
  logging.basicConfig(filename='pbp.log',level=logging.DEBUG)

  yesterday = date.today() - timedelta(1)
  # scrape_day(yesterday.month, yesterday.day, yesterday.year)
  scrape_box_score("dicks")
  # scrape_pbp("https://www.basketball-reference.com/boxscores/pbp/201812040MIA.html")


if __name__ == '__main__':
  main()

  # store and fetch from instead of requesting
  # store_html("https://www.basketball-reference.com/boxscores/201812040MIA.html")
  # get_soup()