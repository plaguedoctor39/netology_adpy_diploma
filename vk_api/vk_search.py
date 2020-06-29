from vk_api.vk_user import VkApi, VkUser
import pprint
import sys
from result_writer import file_writer
from db import results


class VkSearcher(VkUser):
    def __init__(self, user_id=None, age=[18, 22], gender='W'):
        super().__init__(user_id)
        if gender == 'W':
            sex = 1
        elif gender == 'M':
            sex = 2
        else:
            print('Пол введен неверно')
            sys.exit(0)
        self.search_params = {'sort': 0,
                              'count': 1000,
                              'city': self.user_info['city']['id'],
                              'sex': sex,
                              'age_from': age[0],
                              'age_to': age[1],
                              'has_photo': 1,
                              'fields': 'common_count, photo_max_orig, about, activities, books, '
                                        'interests, movies, music, personal',
                              'user_id': self.user_info['id']}

    def search(self):
        top10_results = []
        self.json_ = self.get_response(self.METHOD_USERS_SEARCH, self.search_params)['response']['items']
        self.json_.sort(key=lambda x: x['common_count'])
        # print(len(self.json_))
        try:
            if self.user_info['personal']['smoking'] == 1 or self.user_info['personal']['smoking'] == 2:
                self.del_from_search_list('smoking')
            if self.user_info['personal']['alcohol'] == 1 or self.user_info['personal']['alcohol'] == 2:
                self.del_from_search_list('alcohol')
        except KeyError:
            pass
        # print(len(self.json_))
        self.json_.reverse()
        for usr in self.json_:
            if len(top10_results) >= 10:
                break
            else:
                # print(usr)
                if usr['common_count'] > 0:
                    top10_results.append(usr)
                    continue
                try:
                    if usr['interests'] in self.user_info['interests'] or usr['music'] in self.user_info['music'] or \
                            usr['activities'] in self.user_info['activities']:
                        top10_results.append(usr)
                        continue
                except KeyError:
                    continue
                try:
                    if usr['books'] in self.user_info['books'] or usr['movies'] in self.user_info['movies']:
                        top10_results.append(usr)
                        continue
                except KeyError:
                    continue
        # print(top10_results)
        json_list = self.get_photos(top10_results)

        file_writer(json_list)
        return json_list

    def del_from_search_list(self, key):
        for page in self.json_:
            # print(page)
            try:
                if page['personal'][key] == 5:
                    self.json_.remove(page)
            except KeyError:
                continue

    def get_photos(self, user_list):
        results_json = []
        for usr in user_list:
            json_ = self.get_response(self.METHOD_PHOTOS_GET, {'owner_id': usr['id'],
                                                               'album_id': 'profile',
                                                               'extended': 1})
            new_list = sorted(json_['response']['items'], key=lambda x: x['likes']['count'])
            new_list.reverse()
            new_list = new_list[0:3]
            photos = []
            for photo in new_list:
                photos.append(photo['sizes'][-1]['url'])
            results_json.append({'vk.com/id' + str(new_list[0]['owner_id']): photos})

        return results_json
        # print(json_['response']['items'])


def runner():
    # user_id = input('Введите id пользователя - ')
    age = input('Введите диапазон возраста через - ').split('-')
    gender = input('Введите пол - ')
    searcher = VkSearcher(age=age, gender=gender)
    data = searcher.search()
    params = [searcher.user_info['id'], age, gender]
    results.post_data(params, data)