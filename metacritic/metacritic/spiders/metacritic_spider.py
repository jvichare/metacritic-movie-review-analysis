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
        year_url_list = ['http://www.metacritic.com/browse/movies/score/metascore/discussed/filtered?year_selected={}&sort=desc'.format(x) for x in range(2018, 2017, -1)]

        for url in year_url_list:
            yield Request(url=url, callback=self.parse_year_page)

    def parse_year_page(self, response):
        """
        This function will parse each page containing the 100 most discussed movies
        of that year, and generate a list of URLs and then yield a request to each
        movie page URL.
        """

        # Getting the individual URLs for each movie
        # movie_url_path = response.xpath('//td[@class="title_wrapper"]/div/a/@href').extract()
        # movie_urls_list = ['http://www.metacritic.com' + movie for movie in movie_url_path]

        movie_url_path = response.xpath('//td[@class="title_wrapper"]/div/a/@href').extract()[3]
        movie_urls_list = ['http://www.metacritic.com' + movie_url_path]

        for movie_url in movie_urls_list:
            yield Request(url=movie_url, callback=self.parse_movie_page)

    def parse_movie_page(self, response):
        """
        This function grabs the critic reviews URL and user reviews URL for each movie,
        as well as specific information available on the movie page
        """
        movie = response.xpath('//div[@class="product_page_title oswald"]/h1/text()').extract_first()
        release_date = response.xpath('//span[@class="release_date"]/span[2]/text()').extract_first()
        genre_list = response.xpath('//div[@class="genres"]/span[2]').extract() # have to fix this list
        scores = response.xpath('//a[@class="metascore_anchor"]/div/text()').extract()
        metascore = int(scores[0])
        user_score = float(scores[1])

        # cleaning up the scraped list of genres
        genre_string = ''.join(genre_list)
        genre = re.findall('[A-Z]+[a-z]*\-*[A-Z]*[a-z]*', genre_string) # have to account for Sci-Fi with this regex

        # grabbing the path for critic and user reviews
        critic_review_path = response.xpath('//a[@class="see_all boxed oswald"]/@href').extract()[0]
        user_review_path = response.xpath('//a[@class="see_all boxed oswald"]/@href').extract()[1]
        critic_review_url = 'http://www.metacritic.com' + critic_review_path
        user_review_url = 'http://www.metacritic.com' + user_review_path

        # obtaining the number of user reviews, as each user review page is limited to 100 reviews per page.
        num_user_reviews = response.xpath('//a[@class="see_all boxed oswald"]/text()').extract()[1]
        num_user_reviews = int(re.search('\d+', num_user_reviews).group())

        yield Request(url=critic_review_url, meta={'movie': movie,
                                                    'release_date': release_date,
                                                    'genre': genre,
                                                    'metascore': metascore,
                                                    'user_score': user_score}, callback=self.parse_critic_reviews)

        yield Request(url=user_review_url, meta={'movie': movie,
                                                    'release_date': release_date,
                                                    'genre': genre,
                                                    'metascore': metascore,
                                                    'user_score': user_score}, callback=self.parse_user_reviews)

    def parse_critic_reviews(self, response):
        """
        This function grabs the name of each critic, their individual score, and the headline of their review.
        """
        # Calling back the previous meta attributes
        movie = response.meta['movie']
        release_date = response.meta['release_date']
        genre = response.meta['genre']
        metascore = response.meta['metascore']
        user_score = response.meta['user_score']

        # Getting the review attributes
        reviews = response.xpath('//div[@class="critic_reviews"]//a[@class="no_hover"]/text()').extract()
        usernames = response.xpath('//span[@class="author"]/a/text()').extract()
        review_scores = response.xpath('//div[@class="left fl"]/div/text()').extract()
        user_type = "critic"

        # Writing the fields to the metacritic item
        item = MetacriticItem()

        item['movie'] = movie
        item['release_date'] = release_date
        item['genre'] = genre
        item['metascore'] = metascore
        item['user_score'] = user_score
        item['user_type'] = user_type

        # have to loop over the reviews, usernames, and review_scores list to write them into the object
        for review in reviews:
            item['review'] = review.strip()

        for username in usernames:
            item['username'] = username

        for review_score in review_scores:
            item['review_score'] = int(review_score)

        yield item

    def parse_user_reviews(self, response):
        """
        This function grabs the name of each user, their individual score, and their entire review.
        """
        # reviews = 
        # usernames = response.xpath('//span[@class="author"]/a/text()').extract()
        # review_scores = response.xpath('//div[@class="left fl"]/div/text()').extract()
        # user_type = "user"

        # item = MetacriticItem()

        # item['username'] = 
        # item['user_type'] = user_type
        # item['review_score'] = 
        # item['review'] = 
        pass