from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from twilio.rest import Client

import constants
import records
import scraper
import time

class Alert:
    def __init__(self):
        self.dk_spreads = []
        self.differential = 20
        self.text_entries = {}
        self.sleep_time = 0
        self.next_live_game_check = datetime(2022, 1, 1, 0, 0, 0, 0)

    def check_for_live_games(self):
        now = datetime.now()
        if now < self.next_live_game_check:
            return

        nba_game_times_url = "https://www.google.com/search?q=nba+games+tonight&rlz=1C5CHFA_enUS873US873&oq=nba+games+tonight&aqs=chrome.0.69i59.2874j0j4&sourceid=chrome&ie=UTF-8"
        soup = scraper.get_soup(nba_game_times_url)
        try:
            # Scenario 1: There are games that are live, don't re-check until tomorrow at 8 AM
            spans = soup.findAll('span', {'class':'imso-medium-font'})
            if len(spans) > 0:
                self.sleep_time = 0
                self.next_live_game_check = datetime(now.year, now.month, now.day+1, 8, 0, 0)
                print("There are live games, don't re-check for live games until tomorrow at 8 AM")
                return

            today = soup.find('div', {'class':'imspo_mt__pm-inf imspo_mt__pm-infc imspo_mt__date imso-medium-font'})
            if today is not None:
                today = today.text.strip().lower() == 'today'
            now = datetime.now()

            # Scenario 2: There are no games today. Check tomorrow at 8 AM
            if not today:
                self.next_live_game_check = datetime(now.year, now.month, now.day+1, 8, 0, 0)
                self.sleep_time = (self.next_live_game_check - now).seconds
                print("There are no games today. Check tomorrow at 8 AM")
                return

            # Scenario 3: There are games today but they aren't being played yet. Sleep until 10 minutes before the first game start time
            first_game_time = soup.find('div', {'class':'imspo_mt__ndl-p imspo_mt__pm-inf imspo_mt__pm-infc imso-medium-font'}).text.strip()
            if len(first_game_time) > 0:
                first_game_time = datetime.strptime(first_game_time, '%I:%M %p')
                first_game_time = datetime(now.year, now.month, now.day, first_game_time.hour, first_game_time.minute, 0)
                # sleep until ten minutes before the next game time
                self.sleep_time = (first_game_time - now).seconds - 600
                print("There are games today but they aren't being played yet. Sleep until 10 minutes before the first game start time")
                return

        except:
            print("Failed to check for live games")

    def get_dk_spreads(self, test_mode):
        if test_mode:
            f = open("htmls/dk_with_scores.html", "r")
            soup = f.read()
            f.close()
            soup = BeautifulSoup(soup, "html.parser")
        else:
            draft_kings_sportsbook_url = "https://sportsbook.draftkings.com/leagues/basketball/88670846"
            soup = scraper.get_soup(draft_kings_sportsbook_url)
            # f = open("htmls/dk_with_scores.html", "w+")
            # f.write(soup.prettify())
            # f.close()

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
                self.sleep_time = 10
            # there are no live games, just return and wait for next sleep cycle
            return

        times = []
        quarters = []
        for raw_time in raw_times:
            times.append(raw_time.text.strip())
        for raw_quarter in raw_quarters:
            quarters.append(raw_quarter.text.strip())

        # read per game, so two rows at a time
        self.dk_spreads = []
        for i in range(0, len(trs)-1, 2):
            home_tr = trs[i+1]
            away_tr = trs[i]

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
                self.sleep_time = 10
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

                history = {
                    'home': {
                        'games': 0,
                        'wins': 0,
                        'last_10': '',
                    },
                    'away': {
                        'games': 0,
                        'wins': 0,
                        'last_10': '',
                    }
                }

                for t in history:
                    team = constants.mapping[dk_spread['{0}_team'.format(t)]]
                    historic = historic_records[team]
                    total_games = len(historic)
                    all_wins, all_losses = 0, 0
                    last_ten_wins, last_ten_losses = 0, 0
                    for i, game_record in enumerate(historic):
                        if game_record['win']:
                            all_wins += 1
                        else:
                            all_losses += 1
                        if game_record['largest_deficit'] >= self.differential:
                            history[t]['games'] += 1
                            if game_record['win']:
                                history[t]['wins'] += 1
                        if i >= (total_games-10):
                            if game_record['win']:
                                last_ten_wins += 1
                            else:
                                last_ten_losses += 1
                    history[t]['overall'] = '{0}-{1}'.format(all_wins, all_losses)
                    history[t]['last_10'] = '{0}-{1}'.format(last_ten_wins, last_ten_losses)

                team_down = 'home' if home_score < away_score else 'away'
                team_up =   'home' if home_score > away_score else 'away'

                vs_or_at = 'vs.' if team_down == 'home' else '@'
                differential_text = '0'
                if history[team_down]['games'] > 0:
                    differential_text = "{0}/{1}".format(history[team_down]['wins'], history[team_down]['games'])

                text = """The {} ({}, {}) are down {} {} the {} ({}, {}) in the {} {}\n\nComebacks (down {} or more): {}.\n\nDK ODDS\nML: {}\nSpread: {} at {}""".format(
                    dk_spread['{}_team'.format(team_down)].split(" ")[1],
                    history[team_down]['last_10'],
                    history[team_down]['overall'],
                    dk_spread['{}_score'.format(team_up)]-dk_spread['{}_score'.format(team_down)],
                    vs_or_at,
                    dk_spread['{}_team'.format(team_up)].split(" ")[1],
                    history[team_up]['last_10'],
                    history[team_up]['overall'],
                    dk_spread['quarter'],
                    dk_spread['time_left'],
                    self.differential,
                    differential_text,
                    dk_spread['{}_ml'.format(team_down)],
                    dk_spread['{}_spread'.format(team_down)],
                    dk_spread['{}_spread_odds'.format(team_down)],
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
            print("No games satisfy differential condition")
        for text_entry in self.text_entries:
            text = self.text_entries[text_entry]
            if len(text) > 0:
                # preserve the key in the dict but empty the value, so we won't send this again
                self.text_entries[text_entry] = ""

                if test_mode:
                    print("-----")
                    print(text)
                    print("-----")
                else:
                    for phone_number in constants.phone_numbers:
                        client = Client(constants.twilio_sid, constants.twilio_token)
                        message = client.messages.create(body=text, from_=constants.twilio_number, to=phone_number)
                        print("Message '{0}' sent to {1}.".format(message.body, phone_number))

    def check_for_inactive_players(self):
        # https://sports.yahoo.com/nba/charlotte-hornets-boston-celtics-2022020202/
        pass

    def sleep(self):
        ten_percent = int(.10 * self.sleep_time)
        scraper.sleep(self.sleep_time-ten_percent, self.sleep_time+ten_percent)


def main():
    historic = records.HistoricRecords(False)
    alert = Alert()
    while True:
        alert.check_for_live_games()
        if alert.sleep_time == 0:
            alert.get_dk_spreads(False)
        if alert.sleep_time > 0:
            alert.sleep()
            continue
        historic.get_records()
        alert.check_spreads(historic.Records)
        alert.send_texts(False)

        # Run every 1.5 - 2.5 minutes
        scraper.sleep(120, 150)

main()