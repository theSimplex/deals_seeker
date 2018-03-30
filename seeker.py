import json
import re
import sys
import time
import link_preview

import requests
from bs4 import BeautifulSoup
from telegrammer import Telegrammer


class Seeker(Telegrammer):

    crap_list = ['coupon', 'contest', 'chance', '.99', 'off', 'buy',
                 'spend', 'recipe', 'subscription', 'sweepstakes', 'win',
                 'pre-order', 'shipped', 'purchase', 'deal', 'possibl',
                 'kroger', 'magazine', 'giveaway', ' app ', 'ebook',
                 'cardholder', 'member', 'sale', 'savings', 'as-low',
                 'points', 'survey', 'rewards', 'rental', 'starting', 'kmart',
                 'Kroger', 'guide']

    goodies_list = ['twitter', 'shirt']

    def __init__(self):
        self.sent = []
        with open('log.dat', 'r') as f:
            sent_links = [i.strip('\n') for i in f.readlines()]
            for old_link in sent_links:
                if old_link[-1] == '/':
                    old_link = old_link[:-1]
                self.sent.append(old_link)
            self.sent_tails = [i.split('/')[-1] for i in self.sent]
        with open('config.json') as config_file:
            self.config = json.loads(config_file.read())
        self.message_url = "https://api.telegram.org/bot{}/".format(
            self.config['telegram_token'])
        self.chat = self.config['chat_id']
        self.heartbeat = self.config['heartbeat_id']

    def get_freebies(self):
        ignored = 0
        saved, freebies, bird_food = [], [], []
        sources = [self.parse_couponpro, self.parse_reddit,
                   self.parse_hunt4freebies, self.parse_hip2save]
        for source in sources:
            freebies += source()
        for link in set(freebies):
            if link[-1] == '/':
                link = link[:-1]
            if link in self.sent or self.scan_for_crap(link):
                ignored += 1
                continue
            elif link.split('/')[-1] in self.sent_tails:
                print('Found duplicate: {}'.format(link))
            else:
                self.send_text(link)
                if any(key in self.get_url_info(link) for key in self.goodies_list):
                    self.send_heartbeat(link)
                bird_food.append(link)
                saved.append(link)
        with open('log.dat', 'w') as f:
            if len(self.sent) > 200:
                self.sent = self.sent[-200:]
            for link_ in self.sent + freebies:
                f.write(link_ + '\n')
        self.put_new_tweets_for_the_bird(bird_food)
        print('Ignored {} links as previously sent.'.format(ignored))

    def parse_hip2save(self):
        to_send = []
        page = requests.get('http://hip2save.com/category/freebies/')
        soup = BeautifulSoup(page.content, 'html.parser')
        for article in soup.findAll("h6",
                                    {"class": "entry-title grid-title "}):
            if len(article.findAll("div",
                                   {"class": "es-flag new-flags"})) == 0:
                link = article.find('a').get('href')
                if link:
                    to_send.append(link)
        return to_send

    def parse_reddit(self):
        to_send = []
        headers = {'User-Agent':
                   ('Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36'
                    ' (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36')}
        page = requests.get('https://www.reddit.com/r/freebies/',
                            headers=headers)
        soup = BeautifulSoup(page.content, 'html.parser')
        for topic in soup.findAll("p", {"class": "title"}):
            link = topic.find('a').get('href')
            if link.startswith('/r'):
                continue
            to_send.append(link)
        return to_send

    def parse_hunt4freebies(self):
        to_send = []
        page = requests.get('http://hunt4freebies.com/')
        soup = BeautifulSoup(page.content, 'html.parser')
        for topic in soup.findAll("h2", {"class": "entry-title"}):
            link = topic.find('a').get('href')
            to_send.append(link)
        return to_send

    def parse_couponpro(self):
        to_send = []
        page = requests.get('http://www.couponproblog.com/category/freebies/')
        soup = BeautifulSoup(page.content, 'html.parser')
        for post in soup.findAll("div", {"class": "headline_area"}):
            if len(post.findAll("div", {"class": "expired_imghead"})) == 0:
                link = str(post.find('a')).split('href="')[-1].split('"', 1)[0]
                to_send.append(link)
        return to_send

    def scan_for_crap(self, link):
        info = self.get_url_info(link)
        for crap in self.crap_list:
            if crap in info:
                print('Found crap: {}'.format(link))
                return True
        else:
            return False

    def get_url_info(self, url):
        try:
            preview = link_preview.generate_dict(url)
            return ' '.join(preview.values()) + url
        except Exception as e:
            print('Link failed : {}.'.format(url))
            print(e)
            return url

    def put_new_tweets_for_the_bird(self, urls):
        with open('new.dat', 'w') as f:
            for link_ in urls:
                f.write(link_ + '\n')


while True:
    try:
        go = Seeker()
        go.get_freebies()
        print('Fetched. Going to wait. ({})'.format(time.ctime()))
        time.sleep(900)
    except KeyboardInterrupt:
        raise
    except:
        print('Failure: ', sys.exc_info()[0])
