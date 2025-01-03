# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class MatchItem(scrapy.Item):
    ID = scrapy.Field()
    Ground = scrapy.Field()
    Daytime = scrapy.Field()
    Toss = scrapy.Field()
    Winner = scrapy.Field()
    Bat1 = scrapy.Field()
    Bat2 = scrapy.Field()
    Runs1 = scrapy.Field()
    Runs2 = scrapy.Field()
    Wickets1 = scrapy.Field()
    Wickets2 = scrapy.Field()
