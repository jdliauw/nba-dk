from requests_html import HTMLSession
from bs4 import BeautifulSoup

def get_teams(soup):
  teams = soup.find("div", {"class" : "scorebox"}).findAll("a", {"itemprop" : "name"})
  return teams[1]["href"].split("/")[2], teams[0]["href"].split("/")[2]

def main():
  # session = HTMLSession()
  # response = session.get("https://www.basketball-reference.com/leagues/NBA_2019.html")
  # response.html.render() # render js

  table_ids = [
    "confs_standings_E",
    "confs_standings_W",
    # "team-stats-per_game",
    # "opponent-stats-per_game",
    "team-stats-base",
    "opponent-stats-base",
    # "team-stats-per_poss",
    # "opponent-stats-per_poss",
    # "misc_stats",
    # "team_shooting",
    # "opponent_shooting",
  ]

  for table_id in table_ids:
    # response_html = response.html.find("#{}".format(table_id), first=True).html
    f = open("{}.html".format(table_id), "r")   # DEV
    response_html = f.read()                    # DEV
    soup = BeautifulSoup(response_html, 'html.parser')
    
    if table_id in ["confs_standings_E", "confs_standings_W"]:
      teams = soup.find("table", {"id": "{}".format(table_id)}).find("tbody").findAll("tr")
      conference = "E" if table_id in "confs_standings_E" else "W"
      standings = {conference : {}}

      for team in teams: 
        team_name = team.find("th", {"data-stat": "team_name"}).a["href"].split("/")[2]
        seed = team.find("th", {"data-stat": "team_name"}).text
        seed = int(seed[seed.find("(") + 1 : seed.find(")")])
        standings[conference][team_name] = {"seed": seed}

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

          standings[conference][team_name][data_stat] = val

      # for standing in standings:
      #   for team in standings[standing]:
      #     print(team, standings[standing][team])

      # TODO: Store in DB

    elif table_id in ["team-stats-base", "opponent-stats-base"]:
      teams = soup.find("table", {"id": "{}".format(table_id)}).find("tbody").findAll("tr")
      to = "team" if table_id in "team-stats-base" else "opponent"
      team_stats = { to: {}}
      for team in teams:
        team_name = team.find("td", {"data-stat": "team_name"}).a["href"].split("/")[2]
        rank  = int(team.find("th", {"data-stat" : "ranker"}).text)
        team_stats[to][team_name] = {"rank" : rank }
        
        fields = team.findAll("td")
        for field in fields[1:]:
          team_stats[to][team_name][field["data-stat"]] = float(field.text) if "." in field.text else int(field.text)

      # for to in team_stats:
      #   for team in team_stats[to]:
      #     print(team, team_stats[to][team])

      # TODO: Store in DB

    elif table_id == "team-stats-per_poss": # in [, "opponent-stats-per_poss"]
      

    # elif table_id == "misc_stats":
    # elif table_id == "team_shooting": # in [, "opponent_shooting"]


"""
scraping
controller (2)
message deb/mark
"""

if __name__ == "__main__":
  main()