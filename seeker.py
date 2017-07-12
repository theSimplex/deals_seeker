import sys
import time

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

    def get_freebies(self):
        freebies = self.parse_couponpro() + self.parse_reddit() + self.parse_hunt4freebies()
        for link in set(freebies):
            if link[-1] == '/':
                link = link[:-1]
            if link in self.sent:
                    continue
            self.send_text(link, chat=-1001111779861)
        with open('log.dat', 'w') as f:
            for link_ in list(set(list(self.sent) + freebies)):
                f.write(link_ + '\n')
        
    def parse_reddit(self):
        to_send = []
        page = requests.get('https://www.reddit.com/r/freebies/')
        soup = BeautifulSoup(page.content, 'html.parser')
        for topic in soup.findAll("p", { "class" : "title" }):
            link = topic.find('a').get('href')
            if link.startswith('/r'):
                continue
            to_send.append(link)
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
    try:
        go = Seeker()
        go.get_freebies()
        print('Fetched. Going to wait for an hour. ({})'.format(time.ctime()))
        time.sleep(3600)
    except:
        print('Failure: ', sys.exc_info()[0])
