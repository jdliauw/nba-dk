from bs4 import BeautifulSoup
from datetime import datetime
from requests_html import HTMLSession
import json
import random
import scraper

def main():
  for season in range(1990, 2019):
    url = "https://www.basketball-reference.com/leagues/NBA_{}.html".format(season)
    _ = get_team_stats(url, season)

# https://www.basketball-reference.com/leagues/NBA_2019.html
def get_team_stats(url, season):
  scraper.sleep(3,8)
  table_ids = [
    "confs_standings_E",
    "confs_standings_W",
    "team-stats-base",
    "opponent-stats-base",
    "team-stats-per_poss",
    "opponent-stats-per_poss",
    "misc_stats",
    "team_shooting",
    "opponent_shooting",
  ]

  today = datetime.now().strftime("%Y%m%d")

  session = HTMLSession()
  response = session.get(url, timeout=5)
  if response.status_code != 200:
    # LOG error
    print("")
  response.html.render()

  # when iterating over different tables we don't want to overwrite the
  # team with the previous table stats, therefore use a separate key for each table
  standings = []
  misc_stats = []
  team_stats = {}
  team_per_stats = {}
  shooting_stats = {}

  for table_id in table_ids:
    response_html = response.html.find("#{}".format(table_id), first=True).html
    soup = BeautifulSoup(response_html, 'html.parser')

    if table_id in ["confs_standings_E", "confs_standings_W"]:
      teams = soup.find("table", {"id": "{}".format(table_id)}).find("tbody").findAll("tr")
      conference = "east" if table_id in "confs_standings_E" else "west"

      for team in teams:
        team_name = team.find("th", {"data-stat": "team_name"}).a["href"].split("/")[2]
        seed = team.find("th", {"data-stat": "team_name"}).text
        seed = int(seed[seed.find("(") + 1 : seed.find(")")])
        standing = {"team": team_name, "conference" : conference, "seed": seed, "collected_date": today, "season" : season }

        fields = team.findAll("td")
        for field in fields:
          data_stat = field["data-stat"]

          # convert to proper type
          val = field.text
          if "." in val:
            val = float(val)
          elif val == "—":
            val = 0.0
          else:
            val = int(val)
          
          standing[data_stat] = val

        standings.append(standing)

    elif table_id in ["team-stats-base", "opponent-stats-base", "team-stats-per_poss", "opponent-stats-per_poss"]:
      teams = soup.find("table", {"id": "{}".format(table_id)}).find("tbody").findAll("tr")

      for team in teams:
        team_name = team.find("td", {"data-stat": "team_name"}).a["href"].split("/")[2]
        rank  = int(team.find("th", {"data-stat" : "ranker"}).text)

        if table_id in ["team-stats-base", "opponent-stats-base"]:
          if team_name not in team_stats:
            team_stats[team_name] = {"collected_date" : today, "team" : team_name, "season" : season }

          if table_id == "opponent-stats-base":
            team_stats[team_name]["opp_rank"] = rank
          else:
            team_stats[team_name]["rank"] = rank

          fields = team.findAll("td")
          for field in fields[1:]:
            team_stats[team_name][field["data-stat"]] = float(field.text) if "." in field.text else int(field.text)
        elif table_id in ["team-stats-per_poss", "opponent-stats-per_poss"]:
          if team_name not in team_per_stats:
            team_per_stats[team_name] = {"collected_date" : today, "team" : team_name, "season" : season }

          if table_id == "opponent-stats-per_poss":
            team_per_stats[team_name]["opp_rank"] = rank
          else:
            team_per_stats[team_name]["rank"] = rank

          fields = team.findAll("td")
          for field in fields[1:]:
            team_per_stats[team_name][field["data-stat"]] = float(field.text) if "." in field.text else int(field.text)
        else:
          # TODO: log unknown table type
          print("Unknown table type")

    # this creates a layer of dict keys that we don't care about...alternatively
    # you could iterate and check by key but that's adding time
    elif table_id in ["team_shooting", "opponent_shooting"]:
      teams = soup.find("table", {"id": "{}".format(table_id)}).find("tbody").findAll("tr")
      for team in teams:
        team_name = team.find("td", {"data-stat": "team_name"}).a["href"].split("/")[2]
        if team_name not in shooting_stats:
          shooting_stats[team_name] = {"team" : team_name, "collected_date" : today, "season" : season }

        fields = team.findAll("td")
        for field in fields[1:]:
          shooting_stats[team_name][field["data-stat"]] = float(field.text) if "." in field.text else int(field.text)

    elif table_id == "misc_stats":
      teams = soup.find("table", {"id": "{}".format(table_id)}).find("tbody").findAll("tr")
      for team in teams:
        team_name = team.find("td", {"data-stat": "team_name"}).a["href"].split("/")[2]
        team_misc_stats = {"team": team_name, "collected_date" : today, "season" : season }
        
        fields = team.findAll("td")
        for field in fields[1:]:
          text = field.text
          if field["data-stat"] == "arena_name":
            team_misc_stats[field["data-stat"]] = text
            continue

          if field["data-stat"] in ["net_rtg", "attendance", "attendance_per_g"]:
            text = field.text.replace("+", "").replace(",", "")

          team_misc_stats[field["data-stat"]] = float(text) if "." in text else int(text)
        misc_stats.append(team_misc_stats)

  all_stats = {}
  all_stats["standings"] = standings
  all_stats["team_stats"] = team_stats
  all_stats["team_stats_per_100"] = team_per_stats
  all_stats["team_shooting_stats"] = shooting_stats
  all_stats["misc_stats"] = misc_stats
  return all_stats

if __name__ == "__main__":
  main()