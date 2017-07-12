import json

import requests

TOKEN = "313726066:AAFKTQjDAixSqdxiO16sl11BMIyfBjGpYKA"
URL = "https://api.telegram.org/bot{}/".format(TOKEN)
url = 'https://postmates.com/chicago'


class Telegrammer:

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
        url = URL + "sendMessage?text={}&chat_id={}".format(text, chat_id)
        self.get_url(url)


    def send_text(self, body, chat=None):
        if chat is None:
            text, chat = self.get_last_chat_id_and_text(self.get_updates())
        self.send_message(body, chat)
        print(body)
