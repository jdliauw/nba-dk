from datetime import datetime, timedelta
import argparse
import constants
import logging
import json
import scraper
import util

SCOREBOARD_PREFIX = "https://www.espn.com/nba/scoreboard/_/date/"
MATCHUP_PREFIX = "https://www.espn.com/nba/matchup?gameId="

class HistoricRecords:
    def __init__(self, test_mode):
        self.Records = self.grab_existing_json(constants.RECORDS_JSON)
        self.Games = self.grab_existing_json(constants.GAMES_JSON)
        self.games_to_add = {}
        self.next_check_date = datetime(1970, 1, 1, 0, 0, 0, 0) # default to run
        self.test_mode = test_mode
        logging.basicConfig(filename='logs/records.log', format='%(asctime)s %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=logging.DEBUG)

    def set_next_check_date(self):
        now = datetime.now()
        tomorrow = now + timedelta(1)
        tomorrow = datetime(tomorrow.year, tomorrow.month, tomorrow.day, 8, 0, 0)
        return tomorrow

    def grab_existing_json(self, file):
        f = open(file)
        try:
            j = json.load(f)
        except:
            j = {}
        f.close()
        return j

    def grab_game_ids(self):
        # start_date = datetime(2021, 10, 19)
        start_date = datetime.now() - timedelta(3)
        end_date = datetime.now() - timedelta(1)
        logging.info('-----Grabbing gameids-----')

        self.games_to_add = {}
        formatted_dates = util.get_list_of_formatted_dates(start_date, end_date)
        for formatted_date in formatted_dates:
            # "https://www.espn.com/nba/scoreboard/_/date/20220128"
            url = "{0}{1}".format(SCOREBOARD_PREFIX, formatted_date)
            logging.info('Grabbing soup for {}'.format(url))
            soup = scraper.get_soup(url)

            # DO NOT update self.Games, we will update when we've actually updated the record
            if formatted_date not in self.Games or formatted_date not in self.games_to_add:
                self.games_to_add[formatted_date] = []

            # grab game ids and append
            a_tags = soup.findAll('a', {'class':'AnchorLink Button Button--sm Button--anchorLink Button--alt mb4 w-100'})
            for a_tag in a_tags:
                game_id = a_tag['href'].split("/")
                game_id = str(game_id[len(game_id)-1])
                if game_id not in self.games_to_add[formatted_date] and (formatted_date not in self.Games or game_id not in self.Games[formatted_date]):
                    logging.info('Appending game_id {} to {} games to add list'.format(game_id, formatted_date))
                    self.games_to_add[formatted_date].append(str(game_id))

    def update_records(self):
        logging.info('-----Updating records-----')
        # only grab info from games_to_add, Games ONLY contains gameids that have been added to Records
        for game_date in self.games_to_add:
            logging.info('Updating records for: {}'.format(game_date))
            for game_id in self.games_to_add[game_date]:
                # https://www.espn.com/nba/matchup?gameId=401360182
                url = "{0}{1}".format(MATCHUP_PREFIX, game_id)
                soup = scraper.get_soup(url)
                logging.info('Grabbed soup for {}'.format(url))
                text = soup.prettify()

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
                            "score": home_score,
                            "opp_score": away_score,
                            "win": home_score > away_score,
                        },
                        away:{
                            "game_date": date,
                            "game_id": game_id,
                            "largest_lead": away_lead,
                            "largest_deficit": home_lead,
                            "opp_team": home,
                            "score": away_score,
                            "opp_score": home_score,
                            "win": away_score > home_score,
                        },
                    }

                    # update the records with non-duplicates
                    for team in records:
                        skip = False
                        if team in self.Records:
                            for record in self.Records[team]:
                                if record["game_id"] == game_id:
                                    logging.info("Skipping game_id {}".format(game_id))
                                    skip = True
                                    break
                            if not skip:
                                self.Records[team].append(records[team])
                        else:
                            self.Records[team] = [records[team]]

                        if not skip:
                            logging.info("Appending game_id {} to self.Records (record data) and self.Games (game_id) for team {} and date {}".format(game_id, team, game_date))
                            # only update self.Games if we've added it to the record
                            if game_date not in self.Games:
                                self.Games[game_date] = [game_id]
                            else:
                                self.Games[game_date].append(game_id)
                except Exception as e:
                    logging.error("Error with game_id: {0} with exception {1}".format(game_id, e))
                    continue

    def update_json(self, file, data):
        logging.info('-----Updating JSON {} -----'.format(file))
        f = open(file, "w+")
        json_string = json.dumps(data)
        f.write(str(json_string))
        f.close()

    def get_records(self):
        now = datetime.now()
        if self.test_mode or now < self.next_check_date:
            logging.info('Test mode: {}, now ({}{}{}) < self.next_check_date ({}{}{})'.format(
                self.test_mode,
                now.year,
                now.month,
                now.day,
                self.next_check_date.year,
                self.next_check_date.month,
                self.next_check_date.day,
            ))
            return

        self.next_check_date = self.set_next_check_date()
        if not self.test_mode:
            self.grab_game_ids()
            self.update_records()
            self.update_json(constants.GAMES_JSON, self.Games)
            self.update_json(constants.RECORDS_JSON, self.Records)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('-p', '--prod', action='store_true', help='Are we DOING IT LIVE?')
    args = parser.parse_args()
    r = HistoricRecords(not args.prod)
    r.get_records()