from requests_html import HTMLSession
from bs4 import BeautifulSoup
import json
import random
import scraper

def main():
  # for year in range(1990, 2019):
  for year in [2018]:
    url = "https://www.basketball-reference.com/leagues/NBA_{}.html".format(year)
    scraper.sleep(3,8)
    get_team_stats(url)

def get_team_stats(url):
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

  session = HTMLSession()
  response = session.get(url)
  response.html.render()

  # when iterating over different tables we don't want to overwrite the
  # team with the previous table stats, therefore use a separate key for each table
  standings = []
  misc_stats = []
  team_stats = {}
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
        team_stat = {"team": team_name, "conference" : conference, "seed": seed }

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
          
          team_stat[data_stat] = val

        standings.append(team_stat)

    elif table_id in ["team-stats-base", "opponent-stats-base", "team-stats-per_poss", "opponent-stats-per_poss"]:
      teams = soup.find("table", {"id": "{}".format(table_id)}).find("tbody").findAll("tr")
      team_stats[table_id] = []

      for team in teams:
        team_name = team.find("td", {"data-stat": "team_name"}).a["href"].split("/")[2]
        rank  = int(team.find("th", {"data-stat" : "ranker"}).text)
        invididual_team_stats = { "team" : team_name, "rank" : rank }
        if table_id not in team_stats:
          team_stats[table_id] = []
        
        fields = team.findAll("td")
        for field in fields[1:]:
          invididual_team_stats[field["data-stat"]] = float(field.text) if "." in field.text else int(field.text)
        team_stats[table_id].append(invididual_team_stats)

    # this creates a layer of dict keys that we don't care about...alternatively
    # you could iterate and check by key but that's adding time
    elif table_id in ["team_shooting", "opponent_shooting"]:
      teams = soup.find("table", {"id": "{}".format(table_id)}).find("tbody").findAll("tr")
      for team in teams:
        team_name = team.find("td", {"data-stat": "team_name"}).a["href"].split("/")[2]
        if team_name not in shooting_stats:
          shooting_stats[team_name] = {"team": team_name}

        fields = team.findAll("td")
        for field in fields[1:]:
          shooting_stats[team_name][field["data-stat"]] = float(field.text) if "." in field.text else int(field.text)

    elif table_id == "misc_stats":
      teams = soup.find("table", {"id": "{}".format(table_id)}).find("tbody").findAll("tr")
      for team in teams:
        team_name = team.find("td", {"data-stat": "team_name"}).a["href"].split("/")[2]
        team_misc_stats = {"team": team_name}
        
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
  
  jstandings = json.dumps(standings)
  jteam_stats = json.dumps(team_stats)
  jshooting_stats = json.dumps(shooting_stats)
  jmisc_stats = json.dumps(misc_stats)

  for k, v in enumerate([jteam_stats, jshooting_stats, jstandings, jmisc_stats]):
    f = open("{}.json".format(k), "w+")
    f.write(v)
    f.close()

if __name__ == "__main__":
  main()