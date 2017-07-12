import json

import requests


class Telegrammer:
    def __init__(self):
        with open('config.json') as config_file:
            self.config = json.loads(config_file.read())
        self.message_url = "https://api.telegram.org/bot{}/".format(self.config['telegram_token'])

    def get_url(self, url):
        response = requests.get(url)
        content = response.content.decode("utf8")
        return content

    def get_json_from_url(self, url):
        content = self.get_url(url)
        js = json.loads(content)
        return js

    def get_updates(self):
        url = URL + "getUpdates"
        js = self.get_json_from_url(url)
        return js

    def get_last_chat_id_and_text(self, updates):
        num_updates = len(updates["result"])
        text = updates["result"][-1]["message"]["text"]
        chat_id = updates["result"][-1]["message"]["chat"]["id"]
        return (text, chat_id)

    def send_message(self, text, chat_id):
        url = self.message_url + \
            "sendMessage?text={}&chat_id={}".format(text, chat_id)
        self.get_url(url)

    def send_text(self, body, chat=None):
        if chat is None:
            text, chat = self.get_last_chat_id_and_text(self.get_updates())
        self.send_message(body, chat)
        print(body)
