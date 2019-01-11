# import pdb
import scrapy
from basketball_reference.items import SeasonLog
from collections import OrderedDict
from datetime import datetime

class PlayerGameLogSpider(scrapy.Spider):
    name = "player_game_logs"
    home = "https://www.basketball-reference.com"

    def start_requests(self):
        # the 3 point line was introduced in 1979
        # for year in range(2018, 1978, -1):
        for year in range(2017, 2016, -1):
            season_url = "https://www.basketball-reference.com/leagues/NBA_{}_per_game.html".format(year)
            yield scrapy.Request(url=season_url, callback=self.parse_season)
    
    # example: https://www.basketball-reference.com/leagues/NBA_2018_per_game.html
    def parse_season(self, response):
        # get player urls
        xpath = "//td[contains(@data-stat, 'player')]/a/@href"
        player_urls = response.xpath(xpath).extract()

        # yield scrapy.Request(self.home + player_urls[2], callback=self.parse_player)
        for player_url in player_urls:
            yield scrapy.Request(self.home + player_url, callback=self.parse_player)

    # example: https://www.basketball-reference.com/players/t/tatumja01.html
    def parse_player(self, response):
        """
        we do two things here:
            -  get all the game log links
            -  collect a player's avg(fg%)/distance/year
        """

        # TODO shooting parsing, need splash
        """
        xpath = "//div[contains(@id,"div_shooting")]/table//tbody/tr"
        response.xpath(xpath)
        """
        
        # get player's game log urls
        xpath = "//table[contains(@id,'per_game')]//th[contains(@data-stat,'season')]/a/@href"
        game_log_urls = response.xpath(xpath).extract()

        # yield scrapy.Request(self.home + game_log_urls[0], callback=self.parse_game_log)
        for game_log_url in game_log_urls:
            yield scrapy.Request(self.home + game_log_url, callback=self.parse_game_log)

    # example: https://www.basketball-reference.com/players/t/tatumja01/gamelog/2018
    def parse_game_log(self, response):
        games = response.xpath("//table[contains(@id,'pgl_basic')]/tbody/tr[contains(@id,'pgl_basic')]")
        season = int(response.url[-5:-1])
        player_name_slug = response.url.split('/')[-4]

        stat_rows = []
        for game in games:
            if len(game.xpath('td[contains(@colspan,"23")]').extract()) > 0 or len(game.xpath('td[contains(@colspan,"22")]').extract()) > 0:
                continue

            stat_row = OrderedDict({"season": season})

            # date parsing, break up into year, month, day, and weekday
            stat_row["date"] = game.xpath("td[contains(@data-stat,'date_game')]/a/text()").extract()[0]
            datetime_object = datetime.strptime(stat_row["date"], "%Y-%m-%d")
            stat_row["year"] = int(datetime.strftime(datetime_object, "%Y"))
            stat_row["month"] = int(datetime.strftime(datetime_object, "%m"))
            stat_row["day"] = int(datetime.strftime(datetime_object, "%d"))
            stat_row["weekday"] = datetime.strftime(datetime_object, "%A")

            age  = game.xpath("td[contains(@data-stat,'age')]/text()").extract()[0]
            stat_row["age_years"] = age.split("-")[0]
            stat_row["age_days"] = age.split("-")[1]
            stat_row["home"] = len(game.xpath("td[contains(@data-stat,'game_location')]/text()").extract()) < 1
            stat_row["team"] = game.xpath("td[contains(@data-stat,'team_id')]/a/text()").extract()[0]

            stat_row["opponent"] = game.xpath("td[contains(@data-stat,'opp_id')]/a/text()").extract()[0]
            stat_row["game_started"] = True if game.xpath("td[contains(@data-stat,'gs')]/text()").extract()[0] == '1' else False
            mp = game.xpath("td[contains(@data-stat,'mp')]/text()").extract()[0]
            stat_row["seconds_played"] = int(mp.split(":")[0])*60 + int(mp.split(":")[1]) if ":" in mp else 0
            stat_row["field_goals_made"] = int(game.xpath("td[contains(@data-stat,'fg')]/text()").extract()[0])
            stat_row["field_goals_attempted"] = int(game.xpath("td[contains(@data-stat,'fga')]/text()").extract()[0])
            stat_row["threes_made"] = int(game.xpath("td[contains(@data-stat,'fg3')]/text()").extract()[0])
            stat_row["threes_attempted"] = int(game.xpath("td[contains(@data-stat,'fg3a')]/text()").extract()[0])
            stat_row["free_throws_made"] = int(game.xpath("td[contains(@data-stat,'ft')]/text()").extract()[0])
            stat_row["free_throws_attempted"] = int(game.xpath("td[contains(@data-stat,'fta')]/text()").extract()[0])
            stat_row["offensive_rebounds"] = int(game.xpath("td[contains(@data-stat,'orb')]/text()").extract()[0])
            stat_row["defensive_rebounds"] = int(game.xpath("td[contains(@data-stat,'drb')]/text()").extract()[0])
            stat_row["total_rebounds"] = int(game.xpath("td[contains(@data-stat,'trb')]/text()").extract()[0])
            stat_row["assists"] = int(game.xpath("td[contains(@data-stat,'ast')]/text()").extract()[0])
            stat_row["steals"] = int(game.xpath("td[contains(@data-stat,'stl')]/text()").extract()[0])
            stat_row["blocks"] = int(game.xpath("td[contains(@data-stat,'blk')]/text()").extract()[0])
            stat_row["turnovers"] = int(game.xpath("td[contains(@data-stat,'tov')]/text()").extract()[0])
            stat_row["personal_fouls"] = int(game.xpath("td[contains(@data-stat,'pf')]/text()").extract()[0])
            stat_row["points"] = int(game.xpath("td[contains(@data-stat,'pts')]/text()").extract()[0])
            stat_row["game_score"] = float(game.xpath("td[contains(@data-stat,'game_score')]/text()").extract()[0])

            # not in game logs < 2001
            pm = game.xpath("td[contains(@data-stat,'plus_minus')]/text()")
            stat_row["plus_minus"] = float(pm.extract()[0]) if len(pm) > 0 else 0.0

            fg_pct = game.xpath("td[contains(@data-stat,'fg_pct')]/text()").extract()
            fg3_pct = game.xpath("td[contains(@data-stat,'fg3_pct')]/text()").extract()
            ft_pct = game.xpath("td[contains(@data-stat,'ft_pct')]/text()").extract()
            if len(fg_pct) > 0:
                stat_row["field_goals_percentage"] = float(fg_pct[0]) 
            else:
                stat_row["field_goals_percentage"] = 0.0
 
            if len(fg3_pct) > 0:
                stat_row["threes_percentage"] = float(fg3_pct[0])
            else:
                stat_row["threes_percentage"] = 0.0

            if len(ft_pct) > 0:
                stat_row["free_throws_percentage"] = float(ft_pct[0])
            else:
                stat_row["free_throws_percentage"] = 0.0

            stat_rows.append(stat_row)

        yield SeasonLog(
            player_slug = player_name_slug,
            season = season,
            games = stat_rows
        )