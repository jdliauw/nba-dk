# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class SeasonLog(scrapy.Item):
    """Season log for a given player during a given season"""
    player_slug = scrapy.Field()
    season = scrapy.Field()
    games = scrapy.Field()