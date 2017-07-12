import sys
import time
import json

import requests
from bs4 import BeautifulSoup

from telegrammer import Telegrammer


class Seeker(Telegrammer):
    def __init__(self):
        self.sent = []
        with open('log.dat', 'r') as f:
            sent_links = set([i.strip('\n') for i in f.readlines()])
            for old_link in sent_links:
                if old_link[-1] == '/':
                    old_link = old_link[:-1]
                self.sent.append(old_link)
        with open('config.json') as config_file:
            self.config = json.loads(config_file.read())
        self.message_url = "https://api.telegram.org/bot{}/".format(self.config['telegram_token'])
        self.chat = self.config['chat_id']

    def get_freebies(self):
        freebies = self.parse_couponpro() + self.parse_reddit() + self.parse_hunt4freebies()
        for link in set(freebies):
            if link[-1] == '/':
                link = link[:-1]
            if link in self.sent:
                print('Igonring link as previously sent.({})'.format(link))
                continue
            self.send_text(link)
        with open('log.dat', 'w') as f:
            for link_ in list(set(list(self.sent) + freebies)):
                f.write(link_ + '\n')
        
    def parse_reddit(self):
        to_send = []
        headers = {'User-Agent': ('Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36'
                   ' (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36')}
        page = requests.get('https://www.reddit.com/r/freebies/', headers=headers)
        soup = BeautifulSoup(page.content, 'html.parser')
        for topic in soup.findAll("p", { "class" : "title" }):
            text = topic.find('a').getText().replace('&', 'and')
            link = topic.find('a').get('href')
            if link.startswith('/r'):
                continue
            to_send.append(text + " " + link)
        return to_send

    def parse_hunt4freebies(self):
        to_send = []
        page = requests.get('http://hunt4freebies.com/')
        soup = BeautifulSoup(page.content, 'html.parser')
        for topic in soup.findAll("h2", { "class" : "entry-title" }):
            link = topic.find('a').get('href')
            to_send.append(link)
        return to_send

    def parse_couponpro(self):
        to_send = []
        page = requests.get('http://www.couponproblog.com/category/freebies/')
        soup = BeautifulSoup(page.content, 'html.parser')
        for post in soup.findAll("div", { "class" : "headline_area" }):
            if len(post.findAll("div", { "class" : "expired_imghead" })) == 0:
                link = str(post.find('a')).split('href="')[-1].split('"', 1)[0]
                to_send.append(link)
        return to_send

while True:
    # try:
    go = Seeker()
    go.get_freebies()
    print('Fetched. Going to wait for half an hour. ({})'.format(time.ctime()))
    time.sleep(1800)
    # except KeyboardInterrupt:
    #     raise
    # except:
    #     print('Failure: ', sys.exc_info()[0])
