# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class mainprojecttem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class mains(scrapy.Item):
    title = scrapy.Field()
    text = scrapy.Field()
    image_urls = scrapy.Field()
    date = scrapy.Field()
    file_urls = scrapy.Field()
