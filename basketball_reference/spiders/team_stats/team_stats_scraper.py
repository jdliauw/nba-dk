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
    "team-stats-per_poss",
    "opponent-stats-per_poss",
    "misc_stats",
    "team_shooting",
    "opponent_shooting",
  ]

  for table_id in table_ids:
    # response_html = response.html.find("#{}".format(table_id), first=True)
    f = open("{}.html".format(table_id), "r")
    # html = f.write(response_html.html)
    html = f.read()
    soup = BeautifulSoup(html, 'html.parser')
    
    if table_id in ["confs_standings_E", "confs_standings_W"]:
      teams = soup.find("table", {"id": "{}".format(table_id)}).find("tbody").findAll("tr")
      conference = "E" if table_id in "confs_standings_E" else "W"
      standings = {conference : {}}

      for team in teams: 
        team_name = team.find("th", {"data-stat": "team_name"}).a["href"].split("/")[2]
        seed = team.find("th", {"data-stat": "team_name"}).text
        seed = int(seed[seed.find("(") + 1 : seed.find(")")])
        standings[conference][team_name] = {"seed": seed}

        tds = team.findAll("td")
        for td in tds:
          data_stat = td["data-stat"]

          # convert to proper type
          val = td.text
          if "." in val:
            val = float(val)
          elif val == "—":
            val = 0.0
          else:
            val = int(val)

          standings[conference][team_name][data_stat] = val
      
      for standing in standings:
        for team in standings[standing]:
          print(team, standings[standing][team])


      # print(east_standings)
    # elif table_id == :
    # elif table_id == "team-stats-base":
    # elif table_id == "opponent-stats-base":
    # elif table_id == "team-stats-per_poss":
    # elif table_id == "opponent-stats-per_poss":
    # elif table_id == "misc_stats":
    # elif table_id == "team_shooting":
    # elif table_id == "opponent_shooting":



    f.close()

if __name__ == "__main__":
  main()