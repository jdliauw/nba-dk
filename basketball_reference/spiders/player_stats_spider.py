import scrapy

"""
Season page:
https://www.basketball-reference.com/leagues/NBA_2018_per_game.html # just replace 2018

Loop through players
- collect game log links
- store shooting by distance and yearly stats
- scrape each game log link

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
        # we want two things here:
        # (1) to get all the game log links
        # (2) to extract a players field goal percentage by distance by year

        # TODO: game logs
        game_log_urls = response.xpath("")

        for game_log_url in game_log_urls:
            yield scrapy.Request(game_log_url, callback=self.parse_game_log)

    def parse_game_log(self, response):
        pass






