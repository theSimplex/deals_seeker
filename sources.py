from bs4 import BeautifulSoup

class Sources(object):
    pass

class Hip2Save(Sources):
    urls = ["http://hip2save.com/category/freebies/"]

    @staticmethod
    def process(page):
        to_send = []
        soup = BeautifulSoup(page, 'html.parser')
        for article in soup.findAll("h6",
                                    {"class": "entry-title grid-title "}):
            if len(article.findAll("div",
                                    {"class": "es-flag new-flags"})) == 0:
                link = article.find('a').get('href')
                if link:
                    to_send.append(link)
        return to_send

class FreeFlys(Sources):
    child_urls = ['/Free_Samples/Other', '/Free_Samples/Children', '/Free_Samples/Food', 
                  '/Free_Samples/Health']
    urls = ['http://www.freeflys.com'+ child for child in child_urls]

    @staticmethod
    def process(page):
        links_to_return = []
        soup = BeautifulSoup(page, 'html.parser')
        for topic in soup.findAll("a", {"class": "SO_offerlink"}):
            links_to_return.append(topic.get('href').replace('..', 'http://www.freeflys.com'))
        return links_to_return


class Reddit(Sources):
    urls = ['https://www.reddit.com/r/freebies/']

    @staticmethod
    def process(page):
        to_send = []
        soup = BeautifulSoup(page, 'html.parser')
        for topic in soup.findAll("p", {"class": "title"}):
            link = topic.find('a').get('href')
            if link.startswith('/r'):
                continue
            to_send.append(link)
        return to_send

class Hunt4Freebies(Sources):
    urls = ['http://hunt4freebies.com/']

    @staticmethod
    def process(page):
        to_send = []
        soup = BeautifulSoup(page, 'html.parser')
        for topic in soup.findAll("h2", {"class": "entry-title"}):
            link = topic.find('a').get('href')
            to_send.append(link)
        return to_send


class CouponProBlog(Sources):
    urls = ['http://www.couponproblog.com/category/freebies/']

    @staticmethod
    def process(page):
        to_send = []
        soup = BeautifulSoup(page, 'html.parser')
        for post in soup.findAll("div", {"class": "headline_area"}):
            if len(post.findAll("div", {"class": "expired_imghead"})) == 0:
                link = str(post.find('a')).split('href="')[-1].split('"', 1)[0]
                to_send.append(link)
        return to_send