from argparse import ArgumentParser
from datetime import datetime, date, timedelta

import db
import json
import logging
import scraper

BASE = "https://www.basketball-reference.com"

def run():
  logging.basicConfig(filename="bss.log", level=logging.DEBUG)

  # up to the 15th from the 1st
  start = date(2019, 2, 1)
  end = date(2019, 11, 25) - timedelta(1)
  date_range = []
  for n in range(int((end - start).days) + 1):
    date_range.append(start + timedelta(n))

  """
  # yesterday (instead of date range)
  base = datetime.today()
  date_list = [base - timedelta(days=x) for x in range(0, numdays)]
  yesterday = date.today() - timedelta(1)
  """
  f = open("game_dates.json", "r+")
  game_dates = json.loads(f.read())
  f.close()

  for dt in date_range:
    print("Scraping games on {}".format(dt.strftime("%Y-%m-%d")))
    game_date = dt.strftime("%Y%m%d")

    if game_date in game_dates:
      print("Already scraped games on {}, skipping".format(dt.strftime("%Y-%m-%d")))
      continue

    year = str(dt.year)
    month = dt.month
    month = str(month) if month >= 10 else "0{}".format(month)
    day = str(dt.day)

    scrape_day(month, day, year) # insert happens in scrape_day()
    f = open("game_dates.json", "r+")
    game_dates = json.loads(f.read())
    f.seek(0)
    f.truncate()
    game_dates.append(game_date)
    game_dates.sort()
    f.write(json.dumps(game_dates))
    f.close()

# https://www.basketball-reference.com/boxscores/?month=02&day=6&year=2019
def scrape_day(month, day, year):
  url = "https://www.basketball-reference.com/boxscores/?month={}&day={}&year={}".format(month, day, year)
    # url = "https://www.basketball-reference.com/boxscores/?month=11&day={0}&year=2019".format(day)

  scraper.sleep(3,8) 
  soup = scraper.get_soup(url)
  if soup is None:
    # LOG
    print("no soup for {0}".format(day))
    return

  a_tags = soup.find("div", {"class": "game_summaries"})
  if a_tags is None:
    print("No games on on {0}".format(day))

  a_tags = a_tags.findAll("a")
  for a_tag in a_tags:
    href = a_tag["href"]
    if "boxscore" in href and a_tag.text == 'Box Score':
      base = "https://www.basketball-reference.com"
      bs = scrape_box_score(base + href)
      db.insert(bs, table="games")
      # pbp = scrape_pbp(base + "/boxscores/pbp/" + href.split("/")[-1])
      # db.insert(pbp, table="pbp")

# https://www.basketball-reference.com/boxscores/201902010DEN.html
def scrape_box_score(box_score_url):
  scraper.sleep(3,4)
  soup = scraper.get_soup(box_score_url)
  if soup is None:
    # LOG
    return None
  home, away = get_teams(soup)
  st = soup.find("meta", {"name": "Description"})["content"]
  st = st[st.find("(") + 1 : st.rfind(")")]
  home_score = int(st[st.rfind("(") + 1 : ])
  away_score = int(st[:st.find(")")])

  game_date = soup.find("div", {"class": "scorebox_meta"}).find("div").text
  game_date = datetime.strptime(game_date, "%I:%M %p, %B %d, %Y")
  season = game_date.year
  if game_date.month > 8:
    season += 1
  game_date = game_date.strftime("%Y%m%d")
  stats = []
  
  tables = soup.findAll("table", {"class": ["sortable", "stats_table", "now_sortable"]})

  for table in tables:
    tbody = table.find("tbody")
    trs = tbody.findAll("tr")
    team = table.get("id").split("_")[0].split("-")[1]

    print(team)

    for i, tr in enumerate(trs):
      player_stats = {
        "game_date" : game_date,
        "home": home,
        "opp" : away if team == home else home,
        "team": team,
        "home_score": home_score,
        "away_score": away_score,
        "season" : season,
        }
      tds = tr.findAll("td")
      try:
        pid = tr.th.a["href"].split("/")[-1][:-5]
        starter = True if i < 5 else False

        player_stats["pid"] = pid
        player_stats["starter"] = starter
        

        # Inefficient, but makes the data cleaner
        for index, stat in enumerate(stats):
          if stat["pid"] == pid:
            player_stats = stat
            stats.remove(stats[index])
            break

        # stuff the dict with number vals
        for td in tds:
          if td["data-stat"] == "mp":
            m, s = td.text.split(":")
            player_stats["play_time_raw"] = td.text
            player_stats["mp"] = int(m)
            player_stats["sp"] = int(m)*60 + int(s)
          else:
            player_stats[td["data-stat"]] = scraper.get_number_type(td.text)
        stats.append(player_stats)
      except TypeError:
        pass
      except Exception as e:
        logging.error("Exception {} caught".format(e))

  return stats

# https://www.basketball-reference.com/boxscores/pbp/201902010DEN.html
def scrape_pbp(pbp_url):
  scraper.sleep(3,5)
  soup = scraper.get_soup(pbp_url)
  if soup is None:
    # LOG
    return None
  home, away = get_teams(soup)
  trs = soup.find("table", {"id": "pbp"}).findAll("tr")
  game_date = soup.find("div", {"class": "scorebox_meta"}).find("div").text
  game_date = soup.find("div", {"class": "scorebox_meta"}).find("div").text
  game_date = datetime.strptime(game_date, "%I:%M %p, %B %d, %Y")
  season = game_date.year
  if game_date.month > 8:
    season += 1
  game_date = game_date.strftime("%Y%m%d")

  stats = []
  quarter = 1

  for tr in trs:
    stat = {}
    if tr.get("id") is not None:
      quarter = int(tr.get("id")[1:])

    tds = tr.findAll("td")
    tds_size = len(tds)

    if tds_size == 6:
      for i in range(6):
        td_text = tds[i].text

        # skip if no text
        if len(td_text) <= 1:
          continue

        # PLAYS
        if i in [1, 5]:
          parse_play(tds[i], stat)

        # stuff we don't care about (home/away point differential(extractable))
        elif i in [2, 4]:
          continue

        # SCORES
        elif i == 3:
          away_score, home_score = td_text.split("-")
          stat["away_score"] = int(away_score)
          stat["home_score"] = int(home_score)

        # i == 0
        else: 
          stat["play_time_raw"] = td_text
          minutes, seconds = td_text.split(".")[0].split(":")
          ms = td_text.split(".")[1]
          seconds = float(seconds) + (float(minutes) * 60) + float(ms)
          stat["play_time"] = seconds

    elif tds_size == 2:
      stat["play_time_raw"] = tds[0].text
      minutes, seconds = tds[0].text.split(".")[0].split(":")
      ms = tds[0].text.split(".")[1]
      seconds = float(seconds) + (float(minutes) * 60) + float(ms)
      stat["play_time"] = seconds
      stat["play"] = tds[1].text.replace("'", "")

    if stat:
      stat["quarter"] = quarter
      stat["game_date"] = game_date
      stat["season"] = season
      stat["home"] = home
      stat["away"] = away
      stats.append(stat)

  return stats

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
      stat["shooter"] = a_tags[0]["href"].split("/")[-1][:-5]
      if " makes " in td_text:
        stat["assister"] = a_tags[1]["href"].split("/")[-1][:-5]
      elif " misses " in td_text:
        stat["blocker"] = a_tags[1]["href"].split("/")[-1][:-5]
      else:
        logging.warning("Unknown stat: {}".format(td_text))
    elif len(a_tags) == 1:
      stat["shooter"] = a_tags[0]["href"].split("/")[-1][:-5]
      stat["fg_type"] = 1
    else:
      logging.warning("Unknown type of play: {}".format(td_text))

    # free throws are points scored but do not have "-pt"
    if "-pt" in td_text:
      stat["fg_type"] = int(td_text[td_text.find("-pt")-1 : td_text.find("-pt")])

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
      logging.warning("a_tags len of {}".format(len(td_text)))

  # TIMEOUT
  elif "timeout" in td_text:
    if "Official timeout" in td_text:
      stat["full_timeout"] = "Official"
    elif "20 second timeout" in td_text:
      stat["full_timeout"] = "20s"
    elif any(k in td_text for k in ["no timeout", "Excess timeout", "excessive timeout"]):
      pass

    elif " timeout" in td_text:
      team = td_text[:td_text.find(" full timeout")]
      if len(team) > 0:
        stat["full_timeout"] = scraper.LONG_ABBREV_DICT[team]

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

  # FOULS / TECHS
  elif any(k in td_text for k in ["Away from play", "Clear path", "Def 3 sec", "Defensive three", 
  "Delay tech", "Double technical", "Flagrant foul", "Hanging tech", "Inbound foul", "Loose ball", 
  "Offensive charge", "Offensive foul", "Personal block", "Personal foul", "Personal take foul", 
  "Shooting block foul", "Shooting foul", "Technical foul"]):
    a_tags = td.findAll("a")
    if len(a_tags) >= 1:
      stat["fouler"] = a_tags[0]["href"].split("/")[-1][:-5]
    if len(a_tags) == 2:
      stat["foul_drawer"] = a_tags[1]["href"].split("/")[-1][:-5]

    if "Away from play" in td_text:
      stat["foul_type"] = "away from play"
    elif "Clear path" in td_text:
      stat["foul_type"] = "clear path"
    elif any(k in td_text for k in ["Def 3 sec", "Defensive three"]):
      stat["foul_type"] = "technical: defensive three"
    elif "Delay tech" in td_text:
      stat["tech_type"] = "delay"
    elif "Double technical" in td_text:
      stat["tech_type"] = "double"
    elif "Flagrant foul" in td_text:
      stat["tech_type"] = "flagrant"
    elif "Hanging tech" in td_text:
      stat["tech_type"] = "hanging"
    elif "Inbound foul" in td_text:
      stat["foul_type"] = "inbound"
    elif "Loose ball" in td_text:
      stat["foul_type"] = "loose ball"
    elif any(k in td_text for k in ["Offensive charge", "Offensive foul"]):
      stat["foul_type"] = "personal"
    elif any(k in td_text for k in ["Personal block", "Personal foul", "Personal take foul"]):
      stat["foul_type"] = "personal"
    elif any(k in td_text for k in ["Shooting block foul", "Shooting foul"]):
      stat["foul_type"] = "shooting"
    elif "Offensive foul" in td_text:
      stat["foul_type"] = "offensive"
    elif "Technical foul" in td_text:
      stat["tech_type"] = "normal"
    else:
      logging.warning("Unknown type of foul/tech: {}".format(td_text))  

  # SUBSTITUTIONS
  elif "enters the game" in td_text:
    a_tags = td.findAll("a")
    if len(a_tags) == 2:
      stat["sub_in"] = a_tags[0]["href"].split("/")[-1][:-5]
      stat["sub_out"] = a_tags[1]["href"].split("/")[-1][:-5]
      """
        Lineups unfortunately can't be determined from the "sub in" / "sub out" pbp
        The lineup that starts each quarter is not reported (only for the game (1st))

      if stat["sub_out"] not in lineup:
        print("{} subbed out but not in lineup list: {}".format(stat["sub_out"], lineup))
        logging.warning("{} subbed out but not in lineup list: {}".format(stat["sub_out"], lineup))
      else:
        print(td_text, "\n", lineup)
      
      for i, tuple in enumerate(lineup):
        player, team = tuple
 
        if stat["sub_out"] == player:
          print("{} in for {}".format(stat["sub_in"], stat["sub_out"]))
          lineup[i] = (stat["sub_in"], team)
          break
      """
    else:
      logging.warning("Unknown type of substitution: {}".format(td_text))

  # VIOLATIONS
  elif "Violation " in td_text:
    stat["team_violation"] = "kicked ball"

  elif "ejected from game" in td_text:
    a_tags = td.findAll("a")
    if len(a_tags) == 1:
      stat["ejected"] = a_tags[0]["href"].split("/")[-1][:-5]

  # UNKNOWN
  else:
    logging.warning("Unknown type of play: {}, stat: {}".format(td_text, stat))

def get_teams(soup):
  teams = soup.find("div", {"class" : "scorebox"}).findAll("a", {"itemprop" : "name"})
  return teams[1]["href"].split("/")[2], teams[0]["href"].split("/")[2]

if __name__ == '__main__':
  # pgdb = PostgresDB()
  run()
