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

        # Getting the individual URLs for each movie
        movie_url_path = response.xpath('//td[@class="title_wrapper"]/div/a/@href').extract()
        movie_urls_list = ['http://metacritic.com' + movie for movie in movie_url_path]

        for movie_url in movie_urls_list:
            yield Request(url=movie_url, callback=self.parse_movie_page)

    def parse_movie_page(self, response):
        """
        This function grabs the critic reviews URL and user reviews URL for each movie,
        as well as specific information available on the movie page
        """

        movie = response.xpath('//div[@class="product_page_title oswald"]/h1/text()').extract_first()
        release_date = response.xpath('//span[@class="release_date"]/span[2]/text()').extract_first()
        genre = response.xpath('//div[@class="genres"]/span[2]').extract() # have to fix this list
        metascore = response.xpath('//div[@class="metascore_w larger movie positive"]/text()').extract_first()
        user_score = response.xpath('//div[@class="metascore_w user larger movie positive"]/text()').extract_first()

        # writing the fields to the metacritic item
        item = MetacriticItem()
        
        item['movie'] = movie
        item['release_date'] = release_date
        item['genre'] = genre
        item['metascore'] = metascore
        item['user_score'] = user_score

        yield item

        # grabbing the path for critic and user reviews
        critic_review_path = response.xpath('//a[@class="see_all boxed oswald"]/@href').extract()[0]
        user_review_path = response.xpath('//a[@class="see_all boxed oswald"]/@href').extract()[1]
        critic_review_url = 'http://metacritic.com' + critic_review_path
        user_review_url = 'http://metacritic.com' + user_review_path

        yield Request(url=critic_review_url, callback=self.parse_critic_reviews)

        yield Request(url=user_review_url, callback=self.parse_user_reviews)

    def parse_critic_reviews(self, response):
        pass

    def parse_user_reviews(self, response):
        pass