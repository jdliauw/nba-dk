from argparse import ArgumentParser
from datetime import datetime, date, timedelta
import json
import logging
import scraper

def main():
  yesterday = date.today() - timedelta(1)
  year = yesterday.year
  month = yesterday.month
  day = yesterday.day
  logging.basicConfig(filename="{}-{}-{}.log".format(year, month, day), level=logging.DEBUG)
  scrape_day(month, day, year)

def scrape_day(month, day, year):
  url = "https://www.basketball-reference.com/boxscores/?month={}&day={}&year={}".format(month, day, year)
  soup = scraper.get_soup(url)

  a_tags = soup.find("div", {"class": "game_summaries"}).findAll("a")
  for a_tag in a_tags:
    href = a_tag["href"]
    if "boxscore" in href and a_tag.text == 'Box Score':
      base = "https://www.basketball-reference.com"
      scrape_box_score(base + href)
      scrape_pbp(base + "/boxscores/pbp/" + href.split("/")[-1])

def scrape_box_score(box_score_url):
  scraper.sleep(3,8)
  soup = scraper.get_soup(box_score_url)
  home, away = get_teams(soup)

  game_date = soup.find("div", {"class": "scorebox_meta"}).find("div").text
  datetime_object = datetime.strptime(game_date, "%I:%M %p, %B %d, %Y")
  year = int(datetime.strftime(datetime_object, "%Y"))
  month = int(datetime.strftime(datetime_object, "%m"))
  day = int(datetime.strftime(datetime_object, "%d"))
  weekday = datetime.strftime(datetime_object, "%A")
  stats = []
  
  tables = soup.findAll("table", {"class": ["sortable", "stats_table", "now_sortable"]})

  for table in tables:
    tbody = table.find("tbody")
    trs = tbody.findAll("tr")
    team = table.get("id").split("_")[1].upper()

    for i, tr in enumerate(trs):
      player_stats = {}
      tds = tr.findAll("td")
      try:
        id = tr.th.a["href"].split("/")[-1][:-5]
        starter = True if i < 5 else False

        player_stats["id"] = id
        player_stats["starter"] = starter
        player_stats["team"] = team

        # Inefficient, but makes the data cleaner
        for index, stat in enumerate(stats):
          if stat["id"] == id:
            player_stats = stat
            stats.remove(stats[index])
            break

        # stuff the dict with vals
        for td in tds:
          player_stats[td["data-stat"]] = scraper.get_type(td.text)

        stats.append(player_stats)
      except TypeError:
        pass
      except Exception as e:
        logging.error("Exception {} caught".format(e))

  f = open("./box_score/{}_{}_box_score.json".format(home, away), "w+")
  f.write(json.dumps(stats))
  f.close()

def scrape_pbp(pbp_url):
  scraper.sleep(3,8)
  soup = scraper.get_soup(pbp_url)
  home, away = get_teams(soup)
  trs = soup.find("table", {"id": "pbp"}).findAll("tr")
  stats = []

  for tr in trs:
    tds = tr.findAll("td")
    tds_size = len(tds)
    stat = {}

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

        else: # i == 0
          stat["time"] = td_text

    elif tds_size == 2:
      stat["time"] = tds[0].text
      stat["play"] = tds[1].text

    if stat:
      stats.append(stat)

  f = open("{}_{}_pbp.json".format(home, away), "w+")
  f.write(json.dumps(stats))
  f.close()

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

  # FOULS
  elif any(k in td_text for k in ["Loose ball", "Personal foul", "Personal take foul", "Shooting foul", "Offensive foul", "Technical foul"]):
    a_tags = td.findAll("a")
    if len(a_tags) == 2:
      stat["fouler"] = a_tags[0]["href"].split("/")[-1][:-5]
      stat["foul_drawer"] = a_tags[1]["href"].split("/")[-1][:-5]

      if "Loose ball" in td_text:
        stat["foul_type"] = "loose ball"
      elif any(k in td_text for k in ["Personal foul", "Personal take foul"]):
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

  # UNKNOWN
  else:
    logging.warning("Unknown type of play: {}".format(td_text))

def get_teams(soup):
  teams = soup.find("div", {"class" : "scorebox"}).findAll("a", {"itemprop" : "name"})
  return teams[1]["href"].split("/")[2], teams[0]["href"].split("/")[2]

if __name__ == '__main__':
  main()
