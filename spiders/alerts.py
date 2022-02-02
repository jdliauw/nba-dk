from bs4 import BeautifulSoup
from twilio.rest import Client

import constants
import records
import scraper
import time

class Alert:
    def __init__(self):
        self.dk_spreads = []
        self.differential = 15
        self.text_entries = {}
        self.rerun = False

    def get_dk_spreads(self, test_mode):
        if not test_mode:
            draft_kings_sportsbook_url = "https://sportsbook.draftkings.com/leagues/basketball/88670846"
            soup = scraper.get_soup(draft_kings_sportsbook_url)
            # f = open("htmls/dk_with_scores.html", "w+")
            # f.write(soup.prettify())
            # f.close()
        else:
            f = open("htmls/dk_with_scores.html", "r")
            soup = f.read()
            f.close()
            soup = BeautifulSoup(soup, "html.parser")

        tbody = soup.find('tbody', {'class': 'sportsbook-table__body'})
        trs = tbody.findAll('tr')
        if len(trs) % 2 != 0:
            print("ERROR")

        class_team = {'class': 'event-cell__name-text'}
        class_spread = {'class':'sportsbook-outcome-cell__line'}
        class_spread_odds = {'class':'sportsbook-odds american default-color'}
        class_ml = {'class':'sportsbook-odds american no-margin default-color'}
        class_score = {'class':'event-cell__score'}

        raw_times = tbody.findAll('span', {'class':'event-cell__time'})
        raw_quarters = tbody.findAll('span', {'class':'event-cell__period'})
        if len(raw_times) != len(raw_quarters):
            # there are live games, re-check
            if len(raw_times) > 0 or len(raw_quarters) > 0:
                self.rerun = True
            # there are no live games, just return and wait for next sleep cycle
            return
        times = []
        quarters = []
        for raw_time in raw_times:
            times.append(raw_time.text.strip())
        for raw_quarter in raw_quarters:
            quarters.append(raw_quarter.text.strip())

        # read per game, so two rows at a time
        for i in range(0, len(trs)-1, 2):
            home_tr = trs[i]
            away_tr = trs[i+1]

            home_score = home_tr.find('span', class_score)
            away_score = away_tr.find('span', class_score)

            # game hasn't started
            if home_score is None or away_score is None:
                continue

            try:
                game_spreads = {
                    'home_team': home_tr.find('div', class_team).text.strip(),
                    'home_score': int(home_score.text.strip()),
                    'home_spread': home_tr.find('span', class_spread).text.strip(),
                    'home_spread_odds': home_tr.find('span', class_spread_odds).text.strip(),
                    'home_ml': home_tr.find('span', class_ml).text.strip(),
                    'away_team': away_tr.find('div', class_team).text.strip(),
                    'away_score': int(away_score.text.strip()),
                    'away_spread': away_tr.find('span', class_spread).text.strip(),
                    'away_spread_odds': away_tr.find('span', class_spread_odds).text.strip(),
                    'away_ml': away_tr.find('span', class_ml).text.strip(),
                    'quarter': quarters[i],
                    'time_left': times[i],
                }
                self.dk_spreads.append(game_spreads)
            except:
                self.rerun = True
        return

    def check_spreads(self, historic_records):
        diffs = []
        for dk_spread in self.dk_spreads:
            home_score = dk_spread['home_score']
            away_score = dk_spread['away_score']

            differential = abs(home_score - away_score)
            diffs.append(differential)
            if differential >= self.differential:
                text = ""
                if home_score > away_score:

                    away_historic = historic_records[constants.mapping[dk_spread['away_team']]]
                    wins = 0
                    games = 0
                    for game_record in away_historic:
                        if game_record['largest_deficit'] >= self.differential:
                            games += 1
                            if game_record['win']:
                                wins += 1

                    differential_text = "and have never been down {0} pts.".format(self.differential)
                    if games > 0:
                        differential_text = "and have come back to win {0} out of {1} times when down {2}+.".format(wins, games, self.differential)
                    
                    text = """The {0} (away) are down {1} @ the {2} with {3} left in the {4} {5}. DK ML: {6}, Spread: {7} at {8}""".format(
                        dk_spread['away_team'].split(" ")[1],
                        dk_spread['home_score']-dk_spread['away_score'],
                        dk_spread['home_team'].split(" ")[1],
                        dk_spread['time_left'],
                        dk_spread['quarter'],
                        differential_text,
                        dk_spread['away_ml'],
                        dk_spread['away_spread'],
                        dk_spread['away_spread_odds'],
                    )

                else:

                    home_historic = historic_records[constants.mapping[dk_spread['home_team']]]
                    wins = 0
                    games = 0
                    for game_record in home_historic:
                        if game_record['largest_deficit'] >= self.differential:
                            games += 1
                            if game_record['win']:
                                wins += 1

                    differential_text = "and have never been down {0} pts.".format(self.differential)
                    if games > 0:
                        differential_text = "and have come back to win {0} out of {1} times when down {2}+.".format(wins, games, self.differential)

                    text = """The {0} are down {1} vs. the {2} with {3} left in the {4} {5}. DK ML: {6}, Spread: {7} at {8}""".format(
                        dk_spread['home_team'].split(" ")[1],
                        dk_spread['away_score']-dk_spread['home_score'],
                        dk_spread['away_team'].split(" ")[1],
                        dk_spread['time_left'],
                        dk_spread['quarter'],
                        differential_text,
                        dk_spread['home_ml'],
                        dk_spread['home_spread'],
                        dk_spread['home_spread_odds'],
                    )
                key = dk_spread['home_team']
                # We've already sent a text
                if key in self.text_entries:
                    continue
                else:
                    self.text_entries[key] = text
        
        print(diffs)
        return

    def send_texts(self, test_mode):
        if len(self.text_entries) == 0:
            print("No games satisfy differential")
        for text_entry in self.text_entries:
            text = self.text_entries[text_entry]
            if len(text) > 0:
                # preserve the key in the dict but empty the value, so we won't send this again
                self.text_entries[text_entry] = ""

                if not test_mode:
                    for phone_number in constants.phone_numbers:
                        client = Client(constants.twilio_sid, constants.twilio_token)
                        message = client.messages.create(body=text, from_=constants.twilio_number, to=phone_number)
                        print("Message '{0}' sent to {1}.".format(message.body, phone_number))
                else:
                    print(text)

def main():

    historic = records.get_records()
    alert = Alert()
    while True:
        alert.get_dk_spreads(False)
        alert.check_spreads(historic)
        alert.send_texts(False)

        if alert.rerun:
            time.sleep(10)
            alert.rerun = False
        # Run every 5 minutes
        time.sleep(300)

main()