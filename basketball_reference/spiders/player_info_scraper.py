from bs4 import BeautifulSoup
from requests_html import HTMLSession

import json
import logging
import random
import scraper
import time

def main():
  # logging.basicConfig(filename='player_info_scraper.log',level=logging.DEBUG)
  get_player_info("https://www.basketball-reference.com/players/h/hardeja01.html")

# https://www.basketball-reference.com/leagues/NBA_2018_per_game.html
def get_player_urls(url):
  soup = scraper.get_soup(url)
  players = soup.find("table", {"id": "per_game_stats"}).findAll("tr", {"class" : "full_table"})
  urls = []
  reset = 0

  for player in players:
    player_url = player.findAll("a")[0]["href"]
    player_stats = get_player_info(player_url)
    set_player_stats(player_stats) # TODO: Remove (testing)

    # every 10 players sleep for a bit longer
    if reset == 10:
      reset = 0
      time.sleep(random.randint(25,35) + random.randint(1,100)/100)
    else:
      reset += 1
      time.sleep(random.randint(3,8) + random.randint(1,100)/100)

def get_player_info(url):
  pid = url[url.rfind("/") + 1 : -5]
  all_stats = {"pid" : pid}

  session = HTMLSession()
  response = session.get(url)
  soup = BeautifulSoup(response.text, "html.parser")

  # GAME LOG
  game_log_urls = soup.find("table", {"id": "per_game"}).findAll("th", {"data-stat" : "season"})
  for game_log_url in game_log_urls:
    atag = game_log_url.find("a") 
    if atag is not None:
      year = atag["href"].split("/")[-2]
      all_stats[year] = get_game_log(atag["href"])

  # SHOOTING
  # TODO

  # PLAYER BACKGROUND INFO
  div = soup.find("div", {"itemtype" : "https://schema.org/Person"})
  first, last = div.find("h1", {"itemprop": "name"}).text.split(" ", 1)
  feet, inches = div.find("span", {"itemprop" : "height"}).text.split("-", 1)
  lbs = div.find("span", {"itemprop" : "weight"}).text.replace("lb", "")
  birth_year, birth_month, birth_day = div.find("span", {"itemprop" : "birthDate"})["data-birth"].split("-", 2)
  birth_place = div.find("span", {"itemprop": "birthPlace"}).text
  birth_city = birth_place[birth_place.find("in\xa0") + 3 : birth_place.find(",")]
  birth_state = birth_place[birth_place.find(',') + 2 :]
  
  all_stats["first"] = first
  all_stats["last"] = last
  all_stats["feet"] = feet
  all_stats["inches"] = inches
  all_stats["lbs"] = lbs
  all_stats["birth_year"] = birth_year
  all_stats["birth_month"] = birth_month
  all_stats["birth_day"] = birth_day
  all_stats["birth_city"] = birth_city
  all_stats["birth_state"] = birth_state

  # COLLEGE STATS
  if "College" in div.text:
    response.html.render()
    college_stats_table = response.html.find("#all_college_stats", first=True)
    if college_stats_table is not None: 
      college_stats_table = college_stats_table.html

      # store separately?
      all_stats["college_stats"] = get_college_stats(college_stats_table, pid)

  ps = div.findAll('p')
  for p in ps:
    ptext = p.text

    # position
    if "Position:" in ptext:
      shoots = ptext[ptext.rfind(' ') + 1 : -1]
      if "Point Guard" in ptext:
        position = 1
      elif "Shooting Guard" in ptext: 
        position = 2
      elif "Small Forward" in ptext:
        position = 3
      elif "Power Forward" in ptext:
        position = 4
      elif "Center" in ptext:
        position = 5
      # else:
        # logging.warning("Unknown position {}".format(ptext))
      
      all_stats["shoots"] = shoots
      all_stats["position"] = position
    
    if "High School:" in ptext:
      hs_city = ptext[ptext.find("in\n") + 5 : ptext.find(",")]
      hs_state = ptext[ptext.rfind(' ') + 1 : -1]
      all_stats["hs_city"] = hs_city
      all_stats["hs_state"] = hs_state

    if "Draft:" in ptext:
      pick = ptext[ptext.find("pick, ") + 6 : ptext.rfind("overall") - 3]
      draft_year = ptext[ptext.rfind(',') + 2 : ptext.rfind(',') + 6]
      all_stats["pick"] = pick
      all_stats["draft_year"] = draft_year
    
    for a in p.findAll("a"):
      if "https://twitter.com" in a["href"]:
        all_stats["twitter"] = a["href"].split("/")[-1]

  return all_stats

def get_game_log(game_log_url):
  session = HTMLSession()
  response = session.get(game_log_url)
  soup = BeautifulSoup(response.text, "html.parser")
  playoffs = soup.find("div", {"id": "all_pgl_basic_playoffs"}) != None

  # only render js if playoffs (otherwise there's no need)
  if playoffs:
    response.html.render()
    playoff_table = response.html.find("#pgl_basic_playoffs", first=True)

    if playoff_table is not None:
      playoff_soup = BeautifulSoup(playoff_table.html, "html.parser")
      pgames = playoff_soup.find("tbody").findAll("tr")

      for pgame in pgames:
        # TODO HERE
        print(get_game_stats(pgame))
        break

def get_game_stats(game):
  game_stats = {}

  fields = game.findAll("td")
  for field in fields:
    data_stat = field["data-stat"]
    val = field.text
    # calculate on own, or skip
    if data_stat in ["fg_pct", "fg3_pct", "ft_pct"] or len(val) == 0 or val == " ":
      continue
    if data_stat == "date_game": 
      # 2010-04-18
      y,m,d = val.split("-")
      game_stats["date_year"] = int(y)
      game_stats["date_month"] = int(m)
      game_stats["date_day"] = int(d)
      continue
    elif data_stat in ["team_id", "opp_id"]:
      game_stats[data_stat] = val
      continue
    elif data_stat == "age":
      # 20-235
      y, d = val.split("-")
      game_stats["age_years"] = int(y)
      game_stats["age_days"] = int(d)
      continue
    elif data_stat == "game_location":
      # @
      game_stats["home"] = True if "@" not in val else False
      continue
    elif data_stat == "game_result":
      # L (-8) 
      game_stats["won"] = True if "W" in val else False
      game_stats["margin"] = int(val[val.find("(") + 1 : val.find(")")])
      continue
    elif data_stat == "mp":
      # 16:20
      m, s = val.split(":")
      game_stats["minutes_played"] = int(m)
      game_stats["seconds_played"] = int(s)
      continue
    elif data_stat == "gs":
      game_stats["starter"] = True if int(val) == 1 else 0
      continue
    elif data_stat == "reason":
      game_stats["reason"] = val
      continue
    elif "." in val:
      game_stats[data_stat] = float(val)
      continue
    else:
      game_stats[data_stat] = int(val)

  return game_stats


def get_college_stats(college_stats_table, pid):
  soup = BeautifulSoup(college_stats_table, 'html.parser')
  years = soup.find("tbody").findAll("tr")

  college_stats = []
  for year in years:
    season = year.find("th").text.split("-")[0]
    season_stat = {season: {}}

    fields = year.findAll("td")
    for field in fields:
      data_stat = field["data-stat"]

      if data_stat == "college_id":
        college = field.find("a").text
        season_stat[season]["college"] = college
        continue

      # convert to proper type
      val = field.text
      if len(val) > 0:
        if "." in val:
          val = float(val)
        elif val == "—":
          val = 0.0
        else:
          val = int(val)
      else:
        continue

      season_stat[season][data_stat] = val
    college_stats.append(season_stat)
  return college_stats

def set_player_stats(player_stats):
  jplayer_stats = json.dumps(player_stats)
  f = open("player_stats.json", "w+")
  f.write(jplayer_stats)
  f.close()

if __name__ == "__main__":
  main()