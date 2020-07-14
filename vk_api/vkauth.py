from selenium import webdriver
import re
from urllib.parse import urlencode
import time

URL = 'https://oauth.vk.com/authorize'


class VkAuth:
    def __init__(self):
        self.driver = webdriver.Chrome('vk_api/chromedriver')
        self.auth()

    def auth(self):
        driver = self.driver
        driver.get(get_token())
        # time.sleep(30)
        token_value = 0
        while get_token != 1:
            time.sleep(10)
            try:
                if self.catch_token(self.driver.current_url) == 1:
                    print('Авторизация прошла успешно')
                    return

            except AttributeError:
                continue


    def catch_token(self, path):
        token_pattern = re.compile('token=([0-9]|[A-Za-z])+')
        token = re.search(token_pattern, path)
        self.token = re.sub(r'token=', '', token.group(0))
        with open('token.txt', 'w', encoding='utf8') as f:
            f.write(self.token)
        return 1

    def tearDown(self) -> None:
        self.driver.close()


def get_token():
    params = {
        'client_id': '7399598',
        'display': 'page',
        'scope': 'friends, groups, offline, wall',
        'response_type': 'token',
        'v': '5.52'
    }
    return '?'.join((URL, urlencode(params)))
