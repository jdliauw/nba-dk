import pdb
import scrapy
from basketball_reference.items import SeasonLog
from collections import OrderedDict

"""
This spider collects:
    - player game log statistics by season
    - player field goal percentage averages by distance by year

It works by:
    - providing seasons
        - parsing player urls
            - parsing game log urls
                - parsing and collecting each game log
            - parsing and collecting  avg(fg%)/distance/year
"""

class PlayerStatsSpider(scrapy.Spider):
    name = "player_stats"
    home = "https://www.basketball-reference.com"

    def start_requests(self):
        start_urls = ["https://www.basketball-reference.com/",]
        # the 3 point line was introduced in 1979
        # for year in range(2018, 1978, -1):
        for year in range(2018, 2017, -1):
            season_url = "https://www.basketball-reference.com/leagues/NBA_{}_per_game.html".format(year)
            yield scrapy.Request(url=season_url, callback=self.parse_season)
    
    def parse_season(self, response):
        # get player urls
        xpath = "//td[contains(@data-stat, 'player')]/a/@href"
        player_urls = response.xpath(xpath).extract()

        yield scrapy.Request(self.home + player_urls[2], callback=self.parse_player)
        # for player_url in player_urls:
        #     yield scrapy.Request(self.home + player_url, callback=self.parse_player)

    # example: https://www.basketball-reference.com/players/t/tatumja01
    def parse_player(self, response):
        """
        we do two things here:
            -  get all the game log links
            -  collect a player's avg(fg%)/distance/year
        """

        # TODO shooting parsing
        
        # get player's game log urls
        xpath = "//table[contains(@id,'per_game')]//th[contains(@data-stat,'season')]/a/@href"
        game_log_urls = response.xpath(xpath).extract()

        yield scrapy.Request(self.home + game_log_urls[0], callback=self.parse_game_log)
        # for game_log_url in game_log_urls:
        #     yield scrapy.Request(game_log_url, callback=self.parse_game_log)

    # example: https://www.basketball-reference.com/players/t/tatumja01/gamelog/2018
    def parse_game_log(self, response):
        # pdb.set_trace()
        games = response.xpath("//table[contains(@id,'pgl_basic')]/tbody/tr[contains(@id,'pgl_basic')]")
        season = int(response.url[-5:-1])
        player_name_slug = response.url.split('/')[-3]

        stat_rows = []
        for game in games:
            if len(game.xpath('td[contains(@colspan,"23")]').extract()) > 0 or len(game.xpath('td[contains(@colspan,"22")]').extract()) > 0:
                continue

            date = game.xpath("td[contains(@data-stat,'date_game')]/a/text()").extract()[0]
            age = game.xpath("td[contains(@data-stat,'age')]/text()").extract()[0]
            team = game.xpath("td[contains(@data-stat,'team_id')]/a/text()").extract()[0]
            home = len(game.xpath("td[contains(@data-stat,'game_location')]/text()").extract()) < 1
            opponent = game.xpath("td[contains(@data-stat,'opp_id')]/a/text()").extract()[0]
            gs = True if game.xpath("td[contains(@data-stat,'gs')]/text()").extract()[0] == '1' else False
            mp = game.xpath("td[contains(@data-stat,'mp')]/text()").extract()[0]
            fg = int(game.xpath("td[contains(@data-stat,'fg')]/text()").extract()[0])
            fga = int(game.xpath("td[contains(@data-stat,'fga')]/text()").extract()[0])
            fg_pct = game.xpath("td[contains(@data-stat,'fg_pct')]/text()").extract()
            fg_pct = float(fg_pct[0]) if len(fg_pct) > 0 else None
            fg3 = int(game.xpath("td[contains(@data-stat,'fg3')]/text()").extract()[0])
            fg3a = int(game.xpath("td[contains(@data-stat,'fg3a')]/text()").extract()[0])
            fg3_pct = game.xpath("td[contains(@data-stat,'fg3_pct')]/text()").extract()
            fg3_pct = float(fg3_pct[0]) if len(fg3_pct) > 0 else None
            ft = int(game.xpath("td[contains(@data-stat,'ft')]/text()").extract()[0])
            fta = int(game.xpath("td[contains(@data-stat,'fta')]/text()").extract()[0])
            ft_pct = game.xpath("td[contains(@data-stat,'ft_pct')]/text()").extract()
            ft_pct = float(ft_pct[0]) if len(ft_pct) > 0 else None
            orb = int(game.xpath("td[contains(@data-stat,'orb')]/text()").extract()[0])
            drb = int(game.xpath("td[contains(@data-stat,'drb')]/text()").extract()[0])
            trb = int(game.xpath("td[contains(@data-stat,'trb')]/text()").extract()[0])
            ast = int(game.xpath("td[contains(@data-stat,'ast')]/text()").extract()[0])
            stl = int(game.xpath("td[contains(@data-stat,'stl')]/text()").extract()[0])
            blk = int(game.xpath("td[contains(@data-stat,'blk')]/text()").extract()[0])
            tov = int(game.xpath("td[contains(@data-stat,'tov')]/text()").extract()[0])
            pf = int(game.xpath("td[contains(@data-stat,'pf')]/text()").extract()[0])
            pts = int(game.xpath("td[contains(@data-stat,'pts')]/text()").extract()[0])
            game_score = float(game.xpath("td[contains(@data-stat,'game_score')]/text()").extract()[0])
            plus_minus = float(game.xpath("td[contains(@data-stat,'plus_minus')]/text()").extract()[0])

            stat_rows.append(OrderedDict({
                'Date': date,
                'Season': season,
                'Home Game': home,
                'Team' : team,
                'Opponent': opponent,
                'Started' : gs,
                'Minutes Played' : mp,
                'Field Goals' : fg,
                'Field Goal Attempts' : fga,
                'Field Goal %' : fg_pct,
                'Three Pointers' : fg3,
                'Three Point Attempts' : fg3a,
                'Three Point %' : fg3_pct,
                'Free Throws' : ft,
                'Free Throw Attempts' : fta,
                'Free Throw %' : ft_pct,
                'Offensive Rebounds' : orb,
                'Defensive Rebounds' : drb,
                'Total Rebounds' : trb,
                'Assists' : ast,
                'Steals' : stl,
                'Blocks' : blk,
                'Turnovers' : tov,
                'Personal Fouls' : pf,
                'Points' : pts,
                'Game Score' : game_score,
                'Plus Minus' : plus_minus,
            }))

        yield SeasonLog(
            player = player_name_slug,
            season = season,
            games = stat_rows
        )