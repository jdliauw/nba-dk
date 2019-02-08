from bs4 import BeautifulSoup
from datetime import datetime
from db import PostgresDB
from requests_html import HTMLSession

import json
import logging
import pdb
import random
import scraper
import time

BASE = "https://www.basketball-reference.com"
TODAY = datetime.now().strftime("%Y%m%d")

"""
https://www.basketball-reference.com/players/c/catchha01.html
"""

def run():
  # 1980 - 2000, 2000 - 2019, 1950
  for year in range(1950, 2020):
    print("Starting to parse {} season".format(year))
    url = "https://www.basketball-reference.com/leagues/NBA_{}_per_game.html".format(year)
    get_player_urls(url)

# https://www.basketball-reference.com/leagues/NBA_2018_per_game.html
def get_player_urls(url):
  scraper.sleep(3,5)
  soup = scraper.get_soup(url)
  players = soup.find("table", {"id": "per_game_stats"}).findAll("tr", {"class" : "full_table"})
  db_log = open("db.log", "a")
  start_index = 0

  f = open("pids.txt", "r+")
  pids = f.read().replace("\n", "")
  f.close()

  for i, player in enumerate(players[start_index : ]):
    player_url = player.findAll("a")[0]["href"]

    # Skip pids already read
    pid = player_url.split("/")[-1].split(".")[0]
    if pid in pids:
      continue

    player_url = BASE + player_url

    print(start_index + i, player_url)
    db_log.write("\n{}".format(player_url))
    player_stats = get_player_info(player_url)
    pgdb.insert(stat=player_stats, table="player_info")
    f = open("pids.txt", "a")
    f.write(",{}".format(pid))
    f.close()
    pids += ",{}".format(pid)
  db_log.write("\n\n")
  db_log.close()

# https://www.basketball-reference.com/players/m/mitchdo01.html
def get_player_info(url):
  scraper.sleep(3,5)
  pid = url[url.rfind("/") + 1 : -5]
  all_stats = {}

  session = HTMLSession()
  response = session.get(url, timeout=5)
  session.close()

  if response.status_code != 200:
    # LOG ERROR
    return

  soup = BeautifulSoup(response.text, "html.parser")

   # Need to render for shooting and college stats
  response.html.render()

  # SHOOTING - RENDER REQUIRED
  shooting_stats_table = response.html.find("#shooting", first=True)
  if shooting_stats_table is not None:
    shooting_stats_table = shooting_stats_table.html
    all_stats["player_shooting_stats"] = get_shooting_stats(shooting_stats_table, pid)

  # COLLEGE STATS - RENDER REQUIRED
  college_stats_table = response.html.find("#all_college_stats", first=True)
  if college_stats_table is not None:
    college_stats_table = college_stats_table.html
    all_stats["college_stats"] = get_college_stats(college_stats_table, pid)

  # SALARIES - RENDER REQUIRED
  salaries_table = response.html.find("#all_salaries", first=True)
  if salaries_table is not None:
    salaries_table = salaries_table.html
    all_stats["salaries"] = get_salaries(salaries_table, pid)

  # CONTRACTS - RENDER REQUIRED
  contracts_table = response.html.find("table[id^='contracts']", first=True)
  if contracts_table is not None:
    contracts_table = contracts_table.html
    all_stats["contracts"] = get_contracts(contracts_table, pid)

  # PLAYER BACKGROUND INFO - RENDER NOT REQUIRED
  all_stats["player_info"] = {"pid" : pid }
  div = soup.find("div", {"itemtype" : "https://schema.org/Person"})
  both_names = div.find("h1", {"itemprop": "name"}).text.split(" ", 1)
  first = both_names[0]
  last = both_names[1] if len(both_names) > 1 else ""
  height = div.find("span", {"itemprop" : "height"})
  if height is not None:
    feet, inches = height.text.split("-", 1)
    all_stats["player_info"]["feet"] = int(feet)
    all_stats["player_info"]["inches"] = int(inches)

  weight = div.find("span", {"itemprop" : "weight"})
  if weight is not None:
    lbs = weight.text.replace("lb", "")
    all_stats["player_info"]["lbs"] = int(lbs)
  birth_info = div.find("span", {"itemprop" : "birthDate"})
  if birth_info is not None:
    birth_year, birth_month, birth_day = birth_info["data-birth"].split("-", 2)
    all_stats["player_info"]["birth_year"] = int(birth_year)
    all_stats["player_info"]["birth_month"] = int(birth_month)
    all_stats["player_info"]["birth_day"] = int(birth_day)
  birth_place = div.find("span", {"itemprop": "birthPlace"}).text
  birth_city = birth_place[birth_place.find("in\xa0") + 3 : birth_place.find(",")].replace("'", "")
  birth_state = birth_place[birth_place.find(',') + 2 :].rstrip()
  all_stats["player_info"]["first_name"] = first.replace("'", "")
  all_stats["player_info"]["last_name"] = last.replace("'", "")
 
  all_stats["player_info"]["birth_city"] = birth_city
  all_stats["player_info"]["birth_state"] = birth_state

  ps = div.findAll('p')
  for p in ps:
    ptext = p.text

    # position
    if "Position:" in ptext:
      shoots = ptext[ptext.rfind(' ') + 1 : -1]
      position = ""
      if "Point Guard" in ptext:
        position = "PG"
      if "Shooting Guard" in ptext:
        position += ",SG" if len(position) > 0 else "SG"
      if "Small Forward" in ptext:
        position += ",SF" if len(position) > 0 else "SF"
      if "Power Forward" in ptext:
        position += ",PF" if len(position) > 0 else "PF"
      if "Center" in ptext:
        position += ",C" if len(position) > 0 else "C"
      else:
        pass

      all_stats["player_info"]["shoots"] = shoots
      all_stats["player_info"]["position"] = position

    if "High School:" in ptext:
      hs_city = ptext[ptext.find(" in\n") + 6 : ptext.find(",")].replace("'", "")
      hs_state = ptext[ptext.find(",") + 1 : -1 ].lstrip().rstrip()
      all_stats["player_info"]["hs_city"] = hs_city
      all_stats["player_info"]["hs_state"] = hs_state

    if "Draft:" in ptext:
      pick = ptext[ptext.find("pick, ") + 6 : ptext.rfind("overall") - 3]
      draft_year = ptext[ptext.rfind(',') + 2 : ptext.rfind(',') + 6]

      if pick.isdigit() and draft_year.isdigit():
        all_stats["player_info"]["pick"] = int(pick)
        all_stats["player_info"]["draft_year"] = int(draft_year)

    for a in p.findAll("a"):
      if "https://twitter.com" in a["href"]:
        all_stats["player_info"]["twitter"] = a["href"].split("/")[-1]

  # Let's try to just use the box score since it has all the stats (plus others missing here)
  """
  # GAME LOG
  game_log_urls = soup.find("table", {"id": "per_game"}).findAll("th", {"data-stat" : "season"})
  all_stats["game_logs"] = []
  for game_log_url in game_log_urls:
    atag = game_log_url.find("a") 
    if atag is not None:
      year = atag["href"].split("/")[-2]
      all_stats["game_logs"] += get_game_log(BASE + atag["href"], pid)
  """

  return all_stats

def get_college_stats(college_stats_table, pid):
  soup = BeautifulSoup(college_stats_table, 'html.parser')
  years = soup.find("tbody").findAll("tr")

  college_stats = []
  for year in years:
    season = int(year.find("th").text.split("-")[0]) + 1
    season_stat = {"season": season, "pid": pid}

    fields = year.findAll("td")
    for field in fields:
      data_stat = field["data-stat"]

      if data_stat == "college_id":
        college = field.find("a").text
        season_stat["college"] = college
        continue

      # convert to proper type
      val = scraper.get_converted_type(field.text)
      if val is not None:
        season_stat[data_stat] = val

    college_stats.append(season_stat)
  return college_stats

def get_salaries(salaries_table, pid):
  soup = BeautifulSoup(salaries_table, 'html.parser')
  years = soup.find("tbody").findAll("tr")

  salaries = []
  for year in years:
    season = int(year.find("th").text.split("-")[0]) + 1
    season_salary = {"season": season, "pid": pid, "collected_date": TODAY }

    fields = year.findAll("td")
    for field in fields:
      data_stat = field["data-stat"]

      if data_stat == "team_name":
        team = field.find("a")["href"].split("/")[2]
        season_salary["team"] = team
      elif data_stat == "salary":
        try:
          season_salary["salary"] = field["csk"]
        except:
          pass # this is only

    salaries.append(season_salary)
  return salaries

def get_contracts(contracts_table, pid):
  soup = BeautifulSoup(contracts_table, 'html.parser')
  cols = soup.find("thead")
  if cols is not None:
    cols = cols.findAll("th")
  else:
    # Special case for Sir Dirk Nowitizki!
    cols = soup.find("tr", {"class" : "thead"}).findAll("th")
  vals = soup.find("tbody").findAll("td")
  contracts = {"pid": pid , "collected_date" : TODAY, "contracts" : "" }
  if len(cols) == len(vals):
    for col, val in zip(cols, vals):
      if col["data-stat"].lower() != "team":
        year = int(col["data-stat"][:4]) + 1
        salary = int(val.text.replace("$", "").replace(",", ""))
        year_salary = "{}:{},".format(year, salary)
        contracts["contracts"] += year_salary
      else:
        contracts["team"] = val.find("a")["href"].split("/")[2].replace(".html", "")
    if len(contracts["contracts"]) > 0:
      contracts["contracts"] = contracts["contracts"][:-1]
  return contracts

def get_shooting_stats(shootings_stats_table, pid):
  soup = BeautifulSoup(shootings_stats_table, 'html.parser')
  years = soup.find("tbody").findAll("tr")

  shooting_stats = []
  for year in years:
    season = int(year.find("th").text.split("-")[0]) + 1
    season_stat = {"season": season, "pid" : pid, "collected_date": TODAY }

    fields = year.findAll("td")
    for field in fields:
      data_stat = field["data-stat"]

      # convert to proper type
      val = scraper.get_converted_type(field.text)
      if val is not None:
        season_stat[data_stat] = val

    shooting_stats.append(season_stat)
  return shooting_stats

# for a single fail
def store_player(url):
  pgdb = PostgresDB()
  db_log = open("db.log", "a")
  player_stats = get_player_info(url)
  db_log.write("\n{}".format(url))
  pgdb.insert(stat=player_stats, table="player_info")
  db_log.close()


def hide():
  """
  def get_game_log(game_log_url, pid):
    scraper.sleep(3,5)
    session = HTMLSession()
    response = session.get(game_log_url, timeout=5)
    session.close()

    if response.status_code != 200:
      # LOG ERROR
      return

    soup = BeautifulSoup(response.text, "html.parser")
    year_game_logs = []

    # REGULAR SEASON GAMES
    rs_games = soup.find("table", {"id": "pgl_basic"}).find("tbody").findAll("tr")
    for rs_game in rs_games:
      rs_game_stats = get_game_stats(rs_game, pid)
      if rs_game_stats:
        year_game_logs.append(rs_game_stats)

    # PLAYOFF GAMES
    playoffs = soup.find("div", {"id": "all_pgl_basic_playoffs"}) != None
    # only render js if playoffs (otherwise there's no need)
    if playoffs:
      response.html.render()
      playoff_table = response.html.find("#pgl_basic_playoffs", first=True)

      if playoff_table is not None:
        playoff_soup = BeautifulSoup(playoff_table.html, "html.parser")
        pgames = playoff_soup.find("tbody").findAll("tr")

        for pgame in pgames:
          pgame_stats = get_game_stats(pgame, pid)
          if pgame_stats:
            pgame_stats["playoffs"] = True
            year_game_logs.append(pgame_stats)

    return year_game_logs

  def get_game_stats(game, pid):
    game_stats = {}

    fields = game.findAll("td")
    if len(fields) == 0:
      return None

    game_stats["pid"] = pid
    for field in fields:
      data_stat = field["data-stat"]
      val = field.text
      # calculate on own, or skip
      if len(val) == 0 or val == " ":
        continue
      if data_stat == "date_game":
        # 2010-04-18
        game_stats["game_date"] = val.replace("-", "")
        date_obj = datetime.strptime(val, "%Y-%m-%d")
        if date_obj.month < 8:
          game_stats["season"] = date_obj.year
        else:
          game_stats["season"] = date_obj.year + 1
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
        game_stats["mp"] = int(m)
        game_stats["sp"] = int(s)
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
  """

if __name__ == "__main__":
  pgdb = PostgresDB()
  run()
  pgdb.close()