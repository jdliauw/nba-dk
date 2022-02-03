from datetime import datetime, timedelta
import json
import scraper
import util

SCOREBOARD_PREFIX = "https://www.espn.com/nba/scoreboard/_/date/"
MATCHUP_PREFIX = "https://www.espn.com/nba/matchup?gameId="
RECORDS_JSON = "jsons/records.json"

class HistoricRecords:
    def __init__(self, test_mode):
        self.Records = self.grab_existing_record_history()
        self.next_check_date = self.set_next_check_date()
        self.test_mode = test_mode

    def set_next_check_date(self):
        now = datetime.now()
        tomorrow = now + timedelta(1)
        tomorrow = datetime(tomorrow.year, tomorrow.month, tomorrow.day, 8, 0, 0)
        return tomorrow

    def grab_existing_record_history(self):
        f = open(RECORDS_JSON)
        try:
            records = json.load(f)
        except:
            records = {}
        f.close()
        return records

    def grab_game_ids(self):
        # start_date = datetime(2021, 10, 19)
        start_date = datetime.now() - timedelta(7)
        end_date = datetime.now() - timedelta(1)

        # start of 2021-2022 NBA season (datetime(2021, 10, 19))
        # start_date = datetime(2021, 10, 19)
        formatted_dates = util.get_list_of_formatted_dates(start_date, end_date)
        game_ids = []
        for formatted_date in formatted_dates:
            # "https://www.espn.com/nba/scoreboard/_/date/20220128"
            soup = scraper.get_soup("{0}{1}".format(SCOREBOARD_PREFIX, formatted_date))

            # grab game ids and append
            a_tags = soup.findAll('a', {'class':'AnchorLink Button Button--sm Button--anchorLink Button--alt mb4 w-100'})
            for a_tag in a_tags:
                game_id = a_tag['href'].split("/")
                game_id = game_id[len(game_id)-1]
                if game_id not in game_ids:
                    game_ids.append(str(game_id))

        return game_ids

    def update_records(self, url):
        # https://www.espn.com/nba/matchup?gameId=401360556
        soup = scraper.get_soup(url)
        text = soup.prettify()

        game_id = url.split("=")[1]
        try:
            # grab home/away teams, date
            home = text[text.find("espn.gamepackage.homeTeamName = ")+len("espn.gamepackage.homeTeamName = "):]
            home = home[:home.find(";")].replace('"', '')
            away = text[text.find("espn.gamepackage.awayTeamName = ")+len("espn.gamepackage.awayTeamName = "):]
            away = away[:away.find(";")].replace('"', '')
            date = text[text.find("espn.gamepackage.timestamp = ")+len("espn.gamepackage.timestamp = "):]
            date = date[:date.find(";")].replace('"', '')[:10]
            date = datetime.strptime(date, "%Y-%m-%d") - timedelta(1)
            date = "{0}-{1}-{2}".format(date.year, date.month, date.day)

            home_score = int(soup.find('div', {'class':'score icon-font-before'}).text)
            away_score = int(soup.find('div', {'class':'score icon-font-after'}).text)

            # grab lead/deficits for each team
            # reasonable assumption (?): index 0 is ALWAYS away and index 1 is ALWAYS home
            tds = soup.find("tr", {"data-stat-attr" : "largestLead"}).find_all("td")[1:]
            home_lead = int(tds[1].text.strip())
            away_lead = int(tds[0].text.strip())
            records = {
                home:{
                    "game_date": date,
                    "game_id": game_id,
                    "largest_lead": home_lead,
                    "largest_deficit": away_lead,
                    "opp_team": away,
                    "win": home_score > away_score,
                },
                away:{
                    "game_date": date,
                    "game_id": game_id,
                    "largest_lead": away_lead,
                    "largest_deficit": home_lead,
                    "opp_team": home,
                    "win": away_score > home_score,
                },
            }

            # update the records with non-duplicates
            for team in records:
                skip = False
                if team in self.Records:
                    for record in self.Records[team]:
                        if record["game_id"] == game_id:
                            skip = True
                            break
                    if not skip:
                        print("Appending game_id {}".format(game_id))
                        self.Records[team].append(records[team])
                else:
                    self.Records[team] = [records[team]]
        except Exception as e:
            print("Error with url: {0} with exception {1}".format(url, e))
            pass

    def update_records_json(self):
        f = open(RECORDS_JSON, "w+")
        json_string = json.dumps(self.Records)
        f.write(str(json_string))
        f.close()

    def get_records(self):
        now = datetime.now()
        if self.test_mode or now < self.next_check_date:
            return

        self.next_check_date = self.set_next_check_date()
        game_ids = self.grab_game_ids()

        for k, game_id in enumerate(game_ids):
            self.update_records("{0}{1}".format(MATCHUP_PREFIX, game_id))
        self.update_records_json()
        return self.Records