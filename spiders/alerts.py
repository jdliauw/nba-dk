from bs4 import BeautifulSoup
from datetime import datetime
from twilio.rest import Client

import argparse
import constants
import logging
import records
import scraper


class Alert:
    def __init__(self, test_mode):
        self.client = Client(constants.TWILIO_SID, constants.TWILIO_TOKEN)
        self.dk_spreads = []
        self.differential = 15
        self.text_entries = {}
        self.sleep_time = 0
        self.test_mode = test_mode
        self.next_live_game_check = datetime(2022, 1, 1, 0, 0, 0, 0)
        self.iterations = []
        self.min_sleep_time = 10
        self.texts_sent = {}
        self.now = datetime.now()

    """
    Check for live games. At the completion of each scenario consider whether you need to:
    (1) update the next_live_game_check
    (2) update the sleep time
    (3) log the scenario
    """
    def check_for_live_games(self):
        # scenario 1: we've already checked or are in test mode
        if self.now < self.next_live_game_check or self.test_mode:
            return

        # scenario 2: there are games that are live, don't re-check until tomorrow at 8 AM
        nba_game_times_url = "https://www.google.com/search?q=nba+games+tonight&rlz=1C5CHFA_enUS873US873&oq=nba+games+tonight&aqs=chrome.0.69i59.2874j0j4&sourceid=chrome&ie=UTF-8"
        soup = scraper.get_soup(nba_game_times_url)
        logging.info('Grabbed soup for {}'.format(nba_game_times_url))
        spans = soup.findAll('span', {'class':'imso-medium-font'})
        if len(spans) > 0:
            self.sleep_time = 0
            self.next_live_game_check = datetime(self.now.year, self.now.month, self.now.day+1, 8, 0, 0)
            logging.info('There are live games, don\'t re-check for live games until tomorrow at 8 AM')
            return

        # scenario 3: there are games today but they aren't being played yet. Sleep until 10 minutes before the first game start time
        first_game_time = soup.find('div', {'class':'imspo_mt__ndl-p imspo_mt__pm-inf imspo_mt__pm-infc imso-medium-font'})
        if first_game_time is not None:
            first_game_time = first_game_time.text.strip()
            if len(first_game_time) > 0:
                first_game_time = datetime.strptime(first_game_time, '%I:%M %p')
                first_game_time = datetime(now.year, now.month, now.day, first_game_time.hour, first_game_time.minute, 0)
                # sleep until ten minutes before the next game time
                self.sleep_time = (first_game_time - now).seconds - 600
                logging.info('There are games today but they aren\'t being played yet. Sleep until 10 minutes before the first game start time')
                return

        # scenario 4: there are (1) no live games today or (2) games scheduled for later today. Check tomorrow at 8 AM
        today = soup.find('div', {'class':'imspo_mt__pm-inf imspo_mt__pm-infc imspo_mt__date imso-medium-font'})
        if today is not None:
            today = today.text.strip().lower() == 'today'
        if not today:
            self.next_live_game_check = datetime(now.year, now.month, now.day+1, 8, 0, 0)
            self.sleep_time = (self.next_live_game_check - now).seconds
            logging.info('There are no games today. Check tomorrow at 8 AM')
            return

        # scenario 5: shit's broken
        logging.error('Unknown scenario encountered while checking for live games from Google')
        return

    def get_dk_spreads(self, file):
        if self.test_mode:
            f = open(file, "r")
            soup = f.read()
            f.close()
            soup = BeautifulSoup(soup, "html.parser")
        else:
            draft_kings_sportsbook_url = "https://sportsbook.draftkings.com/leagues/basketball/88670846"
            soup = scraper.get_soup(draft_kings_sportsbook_url)
            logging.info('Grabbed soup for {}'.format(draft_kings_sportsbook_url))

        tbody = soup.find('tbody', {'class': 'sportsbook-table__body'})
        trs = tbody.findAll('tr')
        if len(trs) % 2 != 0:
            logging.warning('Found an uneven amount of rows while parsing DraftKings for spreads')
            self.sleep_time = self.min_sleep_time

        raw_times = tbody.findAll('span', {'class':'event-cell__time'})
        raw_quarters = tbody.findAll('span', {'class':'event-cell__period'})
        if len(raw_times) != len(raw_quarters):
            # there are live games, re-check
            if len(raw_times) > 0 or len(raw_quarters) > 0:
                self.sleep_time = self.min_sleep_time
            # there are no live games, just return and wait for next sleep cycle
            logging.warning('raw_times != raw_quarters, returning with {}s sleep'.format(self.sleep_time))
            return

        times = [raw_time.text.strip() for raw_time in raw_times]
        quarters = [raw_quarter.text.strip() for raw_quarter in raw_quarters]

        self.dk_spreads = []
        class_team = {'class': 'event-cell__name-text'}
        class_spread = {'class':'sportsbook-outcome-cell__line'}
        class_spread_odds = {'class':'sportsbook-odds american default-color'}
        class_ml = {'class':'sportsbook-odds american no-margin default-color'}
        class_score = {'class':'event-cell__score'}

        # read per game, so two rows at a time
        for i in range(0, len(trs)-1, 2):
            home_tr, away_tr = trs[i+1], trs[i]

            # game hasn't started
            home_score, away_score = home_tr.find('span', class_score), away_tr.find('span', class_score)
            if home_score is None or away_score is None:
                continue

            # the following fields are guaranteed to exist
            home_team, away_team = home_tr.find('div', class_team).text.strip(), away_tr.find('div', class_team).text.strip()
            home_score, away_score = int(home_score.text.strip()), int(away_score.text.strip())
            quarter = quarters[i]
            time_left = times[i]

            # the following fields are not guaranteed to exist, so skip if they don't
            try:
                home_spread, away_spread = home_tr.find('span', class_spread).text.strip(), away_tr.find('span', class_spread).text.strip()
                home_spread_odds, away_spread_odds = home_tr.find('span', class_spread_odds).text.strip(), away_tr.find('span', class_spread_odds).text.strip()
                home_ml, away_ml = home_tr.find('span', class_ml).text.strip(), away_tr.find('span', class_ml).text.strip()
            except:
                logging.warning('No odds for {} vs. {} game with a score of {}-{}{} in the {}.'.format(
                    home_team,
                    away_team,
                    home_score,
                    away_score,
                    ' with {} left'.format(time_left),
                    quarter,
                ))
                continue

            game_spreads = {
                'home_team': home_team,
                'home_score': home_score,
                'home_spread': home_spread,
                'home_spread_odds': home_spread_odds,
                'home_ml': home_ml,
                'away_team': away_team,
                'away_score': away_score,
                'away_spread': away_spread,
                'away_spread_odds': away_spread_odds,
                'away_ml': away_ml,
                'quarter': quarter,
                'time_left': time_left,
            }
            self.dk_spreads.append(game_spreads)
        return

    def check_spreads(self, historic_records):
        diffs = {}
        for dk_spread in self.dk_spreads:
            home_score, away_score = dk_spread['home_score'], dk_spread['away_score']

            differential = abs(home_score - away_score)
            diffs['{} vs. {}'.format(dk_spread['home_team'], dk_spread['away_team'])] = differential
            if differential >= self.differential:
                text = ""

                history = {
                    'home': {
                        'games': 0,
                        'last_10': '',
                        'overall': '',
                        'margins': {
                            'wins': 0,
                        },
                    },
                    'away': {
                        'games': 0,
                        'last_10': '',
                        'overall': '',
                        'margins': {
                            'wins': 0,
                        },
                    }
                }

                for t in history:
                    team = constants.TEAM_MAPPING[dk_spread['{0}_team'.format(t)]]
                    historic = historic_records[team]
                    total_games = len(historic)
                    all_wins, all_losses = 0, 0
                    last_ten_wins, last_ten_losses = 0, 0
                    margins = {'wins':0}
                    margin = 5

                    for i, game_record in enumerate(historic):
                        # W/L record
                        if game_record['win']:
                            all_wins += 1
                        else:
                            all_losses += 1

                        # W/L for L10
                        if i >= (total_games-10):
                            if game_record['win']:
                                last_ten_wins += 1
                            else:
                                last_ten_losses += 1

                        # Create raw {final score deficit : count} mapping
                        if game_record['largest_deficit'] >= self.differential:
                            history[t]['games'] += 1
                            final_differential = game_record['score'] - game_record['opp_score']
                            if final_differential > 0:
                                if game_record['win']:
                                    margins['wins'] += 1
                                else:
                                    logging.error('Game differential calculation error')
                            else:
                                final_differential = abs(final_differential)
                                for diff in range(5, self.differential + margin, margin):
                                    if final_differential > diff - margin and final_differential <= diff:
                                        if diff in margins:
                                            margins[diff] += 1
                                        else:
                                            margins[diff] = 1

                    history[t]['overall'] = '{0}-{1}'.format(all_wins, all_losses)
                    history[t]['last_10'] = '{0}-{1}'.format(last_ten_wins, last_ten_losses)

                    # Format the margins output, the range() above cannot take into account games lost by more than the
                    # set differential, so subtract the sum of each margins game from the total number of games
                    largest = 0
                    sum_margin_games = 0
                    for diff in margins:
                        sum_margin_games += margins[diff]
                        if diff == 'wins':
                            history[t]['margins']['wins'] = margins[diff]
                        else:
                            history[t]['margins']['<={}'.format(diff)] = margins[diff]
                            if diff > largest:
                                largest = diff
                    history[t]['margins']['<={}'.format(largest + margin)] = history[t]['games'] - sum_margin_games

                # Text formatting
                team_down, team_up = 'home' if home_score < away_score else 'away', 'home' if home_score > away_score else 'away'
                vs_or_at = 'vs.' if team_down == 'home' else '@'
                differential_text = "{0} in {1} games.".format(history[team_down]['margins'], history[team_down]['games']) if history[team_down]['games'] > 0 else 'None'

                text = """The {} ({}, {}) are down {} {} the {} ({}, {}) in the {} ({} left)\n\nMargin history (down {} or more): {}.\n\nDK ODDS\nML: {}\nSpread: {} at {}""".format(
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
                # we've already sent a text
                if key in self.text_entries:
                    continue
                else:
                    self.text_entries[key] = text
        
        logging.info('Game score diffs: {}'.format(diffs))
        return

    def send_texts(self):
        if len(self.text_entries) == 0:
            logging.info('No games satisfy differential condition')
        for text_entry in self.text_entries:
            text = self.text_entries[text_entry]
            if len(text) > 0:
                # preserve the key in the dict but empty the value, so we won't send this again
                self.text_entries[text_entry] = ""

                if self.test_mode:
                    logging.info("Message: '{0}'".format(text))
                else:
                    for phone_number in constants.PHONE_NUMBERS:
                        message = self.client.messages.create(body=text, from_=constants.TWILIO_NUMBER, to=phone_number)
                        text_sent_date_key = self.now.strftime('%Y-%m-%d')
                        if text_sent_date_key not in self.texts_sent:
                            self.text_sent[text_sent_date_key] = 0
                        else:
                            self.text_sent[text_sent_date_key] += 1
                        logging.info("Message '{0}' sent to {1}.".format(message.body, phone_number))

    def check_for_inactive_players(self):
        # https://sports.yahoo.com/nba/charlotte-hornets-boston-celtics-2022020202/
        pass

    def sleep(self):
        ten_percent = int(.10 * self.sleep_time)
        scraper.sleep(self.sleep_time-ten_percent, self.sleep_time+ten_percent)
        alert.sleep_time = 0

    """
    Terminate script if (1) we've sent the max text limit or (2) we've consecutively failed 10 times
    """
    def check_terminate(self):
        num_consecutive = 10
        if self.test_mode or len(self.iterations) < num_consecutive:
            return False

        text_sent_date_key = self.now.strftime('%Y-%m-%d')
        if text_sent_date_key in self.texts_sent and self.texts_sent[text_sent_date_key] >= 8 * len(constants.PHONE_NUMBERS):
            error_message = 'Reached maximum texts sent per day: {}'.format(self.texts_sent[text_sent_date_key])
            self.client.messages.create(body=error_message, from_=constants.TWILIO_NUMBER, to=constants.MY_PHONE_NUMBER)
            return True

        consecutive_fails = True
        for i in range(len(self.iterations)-1, len(self.iterations)-num_consecutive, -1):
            if i-1 >= 0:
                diff = self.iterations[i] - self.iterations[i-1]
                if diff.total_seconds() > self.min_sleep_time:
                    consecutive_fails = False
                    self.iterations = self.iterations[-1:]
                    break

        if consecutive_fails:
            error_message = '10 consecutive sleep times of less than {}s'.format(self.min_sleep_time)
            self.client.messages.create(body=error_message, from_=constants.TWILIO_NUMBER, to=constants.MY_PHONE_NUMBER)
            logging.Error('Message {} sent to {}'.format(error_message, constants.MY_PHONE_NUMBER))

        return consecutive_fails



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('-p', '--prod', action='store_true', help='Are we DOING IT LIVE?')
    parser.add_argument('-f', '--file', default='', help='Pass an html to read')
    args = parser.parse_args()

    file = args.file if not args.prod and len(args.file) > 0 else 'htmls/dk_with_scores.html'

    # set up logging
    logging.basicConfig(filename='logs/alerts.log', format='%(asctime)s %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=logging.DEBUG)

    historic = records.HistoricRecords(not args.prod)
    alert = Alert(not args.prod)

    while True:
        alert.now = datetime.now()
        alert.iterations.append(alert.now)
        if alert.check_terminate():
            break

        logging.info('Iteration at {}'.format(alert.now.strftime('%H:%M:%S')))
        alert.check_for_live_games()
        if alert.sleep_time == 0:
            alert.get_dk_spreads(file)
        if alert.sleep_time > 0:
            alert.sleep()
            continue
        historic.get_records()
        alert.check_spreads(historic.Records)
        alert.send_texts()

        # run every 1.5 - 2.5 minutes
        scraper.sleep(120, 150)