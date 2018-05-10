from scrapy import Spider, Request
from metacritic.items import MetacriticItem
import re

class MetacriticSpider(Spider):
    name = 'metacritic_spider'
    allowed_urls = ['http://www.metacritic.com']
    start_urls = ['http://www.metacritic.com/browse/movies/score/metascore/discussed/filtered?year_selected=2018&sort=desc']

    def parse(self, response):
        """
        This function constructs a list of all the URLs for the most discussed movies
        from years 2010 to 2018, and will yield requests for each of them.
        """
        year_url_list = ['http://www.metacritic.com/browse/movies/score/metascore/discussed/filtered?year_selected={}&sort=desc'.format(x) for x in range(2018, 2009, -1)]

        for url in year_url_list:
            yield Request(url=url, callback=self.parse_year_page)

    def parse_year_page(self, response):
        """
        This function will parse each page containing the 100 most discussed movies
        of that year, and generate a list of URLs and then yield a request to each
        movie page URL.
        """
        movie_list = response.xpath('//td[@class="title_wrapper"]/div/a/text()').extract()

        for movie in movie_list:
            print(movie)

