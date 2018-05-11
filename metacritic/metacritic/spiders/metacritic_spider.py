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
        movie_urls_list = ['http://www.metacritic.com' + movie for movie in movie_url_path]

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
        metascore = int(scores[0]) # integer from 0 -> 100
        user_score = float(scores[1]) # number between 0 -> 10, that is why I use 
                                      # float() instead of int()

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
                                                    'user_score': user_score,
                                                    'num_user_reviews': num_user_reviews}, callback=self.parse_user_reviews)

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

        # Getting the review attributes in a list
        reviews = response.xpath('//div[@class="critic_reviews"]//a[@class="no_hover"]/text()').extract()
        usernames = response.xpath('//span[@class="author"]/a/text()').extract()
        review_scores = response.xpath('//div[@class="left fl"]/div/text()').extract()

        # Singular attribute, not going to change within this function
        user_type = "critic"

        # Writing the fields to the metacritic item
        item = MetacriticItem()

        # Have to loop the number of critic reviews
        for i in list(range(0, len(usernames) - 1)):
            item['movie'] = movie
            item['release_date'] = release_date
            item['genre'] = genre
            item['metascore'] = metascore
            item['user_score'] = user_score
            item['user_type'] = user_type

            item['review'] = reviews[i].strip()
            item['username'] = usernames[i]
            item['review_score'] = int(review_scores[i])

            yield item

    def parse_user_reviews(self, response):
        """
        This function grabs the name of each user, their individual score, and their entire review.
        """        
        # Calling back the previous meta attributes
        movie = response.meta['movie']
        release_date = response.meta['release_date']
        genre = response.meta['genre']
        metascore = response.meta['metascore']
        user_score = response.meta['user_score']

        # Singular attribute, not going to change within the context of this function
        user_type = "user"

        # User reviews and score attributes
        reviews = user_revews = response.xpath('//span[@class="blurb blurb_expanded"]/text()').extract()
        usernames = response.xpath('//span[@class="author"]/a/text()').extract()
        review_scores = response.xpath('//div[@class="left fl"]/div/text()').extract()

        item = MetacriticItem()

        for i in list(range(0, len(usernames) - 1)):
            item['movie'] = movie
            item['release_date'] = release_date
            item['genre'] = genre
            item['metascore'] = metascore
            item['user_score'] = user_score
            item['user_type'] = user_type

            item['review'] = reviews[i].strip()
            item['username'] = usernames[i]
            item['review_score'] = float(review_scores[i]) # they are a decimal for now,
                                                           # will convert during cleanup

            yield item
        
        # There are most certainly more pages (100 comments per page), getting pattern
        # of the following urls
        num_user_reviews = response.meta['num_user_reviews']
        rev_per_page = 100

        num_pages = num_user_reviews // rev_per_page # not adding one since metacritic actually
                                                     # indexes their successive review pages
                                                     # starting from 0 (i.e. page 1 = '?page=0')

        # starting the range at 1 because we already scraped the first page ('page=0') of reviews
        following_urls = [response.url + '?page={}'.format(x) for x in range(1, num_pages + 1)] 

        for url in following_urls:
            yield Request(url=url, meta={'movie': movie,
                                            'release_date': release_date,
                                            'genre': genre,
                                            'metascore': metascore,
                                            'user_score': user_score}, callback=self.parse_following_review_page)

    def parse_following_review_page(self, response):
        """
        This function is the same as the parsing of the user reviews page, ignoring the multiple
        requests for the following review pages.
        """        
        # Calling back the previous meta attributes
        movie = response.meta['movie']
        release_date = response.meta['release_date']
        genre = response.meta['genre']
        metascore = response.meta['metascore']
        user_score = response.meta['user_score']

        # Singular attribute, not going to change within the context of this function
        user_type = "user"

        # User reviews and score attributes
        reviews = user_revews = response.xpath('//span[@class="blurb blurb_expanded"]/text()').extract()
        usernames = response.xpath('//span[@class="author"]/a/text()').extract()
        review_scores = response.xpath('//div[@class="left fl"]/div/text()').extract()

        item = MetacriticItem()

        for i in list(range(0, len(usernames) - 1)):
            item['movie'] = movie
            item['release_date'] = release_date
            item['genre'] = genre
            item['metascore'] = metascore
            item['user_score'] = user_score
            item['user_type'] = user_type

            item['review'] = reviews[i].strip()
            item['username'] = usernames[i]
            item['review_score'] = float(review_scores[i]) # they are a decimal for now,
                                                           # will convert during cleanup

            yield item