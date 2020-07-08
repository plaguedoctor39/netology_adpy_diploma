from vk_api import constants, vkauth, vk_search
import sys
import json
import requests

import time


class VkApi:
    API_VERSION_VK = constants.API_VERSION_VK
    URL_VK = constants.URL_VK
    TOKEN = constants.TOKEN
    PARAMS = constants.PARAMS
    METHOD_GROUPS_GET = 'groups.get'
    METHOD_USERS_GET = 'users.get'
    METHOD_USERS_SEARCH = 'users.search'
    METHOD_PHOTOS_GET = 'photos.get'

    def __init__(self, user_id=None):
        self.PARAMS = {
            'access_token': self.TOKEN,
            'v': self.API_VERSION_VK
        }

    def get_url(self, method):
        return f'{self.URL_VK}{method}'

    def get_response(self, method, params=None):
        if params is None:
            current_params = self.PARAMS
        else:
            current_params = self.PARAMS
            current_params.update(params)
        response = requests.get(self.get_url(method), current_params)
        time.sleep(constants.TIME_SLEEP)
        json_ = response.json()
        # print(json_)
        try:
            if json_['error']['error_code'] == 5:
                session = vkauth.VkAuth()
                session.auth()
                vk_search.runner()

        except KeyError:
            pass

        return json_


class VkUser(VkApi):

    def __init__(self, user_id=None):
        super().__init__(user_id)

        self.user_info = self.get_info(user_id)
        self.user_info['groups'] = self.get_groups(self.user_info['id'])
        self.PARAMS.update({'user_id': self.user_info['id']})
        print(self.user_info)

    def get_groups(self, user_id=None):
        json_ = self.get_response(self.METHOD_GROUPS_GET, {'user_id': user_id})
        return json_['response']['items']

    def get_info(self, user_id=None):
        user_info = self.get_response(self.METHOD_USERS_GET, {'fields': 'about, activities, books, city, '
                                                                        'interests, movies, music, personal, '
                                                                        'sex',
                                                              'user_ids': user_id})
        print('~ получаем информацию о пользователе')
        try:
            # Проверяем правильность введенного id
            if 'deactivated' in user_info['response'][0]:
                print(f'Пользователь {user_info["response"][0]["id"]} удален или забанен')
                sys.exit()
        except KeyError:
            # print(user_info)
            print(f'Пользователя с id {user_id} нету')
            sys.exit()
        return user_info['response'][0]
