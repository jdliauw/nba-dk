# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class BasketballReferenceItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class SeasonLog(scrapy.Item):
    """Season log for a given player during a given season"""
    player = scrapy.Field()
    player_slug = scrapy.Field()
    season = scrapy.Field()
    games = scrapy.Field()