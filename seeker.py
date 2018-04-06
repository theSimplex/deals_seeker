import json
import re
import sys
import time
import link_preview

import requests
from bs4 import BeautifulSoup
from telegrammer import Telegrammer
from async_parser import AsyncParser


headers = {'User-Agent':
          ('Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36'
           ' (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36')}


class Seeker(Telegrammer):

    crap_list = ['coupon', 'contest', 'chance', '.99', 'off', 'buy',
                 'spend', 'recipe', 'subscription', 'sweepstakes', 'win',
                 'pre-order', 'shipped', 'purchase', 'deal', 'possibl',
                 'kroger', 'magazine', 'giveaway', 'ebook',
                 'cardholder', 'member', 'sale', 'savings', 'as-low',
                 'points', 'survey', 'rewards', 'rental', 'starting', 'kmart',
                 'Kroger', 'guide', 'only', 'app', 'regular', 'just', '-at-',
                 'printable', 'recipe', '_at_']

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
        parser = AsyncParser()
        start = time.time()
        freebies = parser.parse()
        stop = time.time() - start
        print('Found {} links in {}s.'.format(len(freebies), stop))
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

    def scan_for_crap(self, link):
        info = self.get_url_info(link)
        for crap in self.crap_list:
            if crap.upper() in info.upper():
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
        print('Cycle is done. Going to wait. ({})'.format(time.ctime()))
        time.sleep(900)
    except KeyboardInterrupt:
        raise
    except:
        print('Failure: ', sys.exc_info()[0])
