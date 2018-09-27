import scrapy

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
        # the 3 point line was introduced in 1979
        for year in range(2018, 1978, -1):
            season_url = "https://www.basketball-reference.com/leagues/NBA_{}_per_game.html".format(year)
            yield scrapy.Request(url=season_url, callback=self.get_player_list_from_season)
    
    def get_player_list_from_season(self, response):
        # get season end year from url
        # season = response.url.split("/")[-1][4:8]

        # extract player links
        player_urls = response.xpath("//td[contains(@data-stat, 'player')]/a/@href").extract()

        for player_url in player_urls:
            yield scrapy.Request(player_url, callback=self.parse_player_url)

    def parse_player_url(self, response):
        """
        we do two things here:
            -  get all the game log links
            -  collect a player's avg(fg%)/distance/year
        """

        # TODO shooting parsing
        

        # TODO game logs
        xpath = "//table[contains(@id,'per_game')]//th[contains(@data-stat,'season')]/a/@href"
        game_log_urls = response.xpath(xpath).extract()

        for game_log_url in game_log_urls:
            yield scrapy.Request(game_log_url, callback=self.parse_game_log)

    def parse_game_log(self, response):
        pass






