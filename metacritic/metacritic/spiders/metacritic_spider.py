from scrapy import Spider, Request
from metacritic.items import MetacriticItem
import re

class MetacriticSpider(Spider):
    name = 'metacritic_spider'
    allowed_urls = ['http://www.metacritic.com']