# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class MetacriticItem(scrapy.Item):
    movie = scrapy.Field()
    release_date = scrapy.Field()
    genre = scrapy.Field()
    metascore = scrapy.Field()
    user_score = scrapy.Field()
    username = scrapy.Field()
    user_type = scrapy.Field()
    review_score = scrapy.Field()
    review = scrapy.Field()



