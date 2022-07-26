import logging

from Config import Config
import requests

class Interface:
    config = Config("test.db")

    def __init__(self):
        self.config = Config("test.db")

    def search(self, addr):
        url = self.config['url']
        token = 'Token ' + self.config['token']
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'Authorization': token}

        lang = self.config['lang']
        json_data = {'query': addr, 'language': lang}

        response = requests.post(url, headers=headers, json=json_data)
        logging.debug("got response")
        return response


