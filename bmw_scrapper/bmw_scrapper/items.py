# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class CarItem(scrapy.Item):
    registration = scrapy.Field()
    model = scrapy.Field()
    name = scrapy.Field()
    registered = scrapy.Field()
    mileage = scrapy.Field()
    engine = scrapy.Field()
    range = scrapy.Field()
    exterior = scrapy.Field()
    fuel = scrapy.Field()
    transmission = scrapy.Field()
    upholstery = scrapy.Field()
