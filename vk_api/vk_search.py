from vk_api.vk_user import VkApi, VkUser, constants
import pprint
import sys
from result_writer import file_writer
from db import results


class VkSearcher(VkUser):
    def __init__(self, user_id=None, age=[18, 22], gender='W'):
        super().__init__(user_id)
        if gender.upper() == 'W':
            sex = 1
        elif gender.upper() == 'M':
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

    def search(self, next10=False):
        if next10:
            return self.get_top10()
        else:
            self.json_ = self.get_response(self.METHOD_USERS_SEARCH, self.search_params)['response']['items']
            self.sort_searcher()
            return self.get_top10()
        # print(self.json_)

    def get_top10(self):
        top10_results = []
        for usr in self.json_:
            if self.get_info(usr['id'])['is_closed']:
                continue
            if results.check_blacklist(usr['id']) == 1:
                continue
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
        self.del_from_search_list(drop=True)
        file_writer(json_list)
        return json_list

    def sort_searcher(self):
        # TODO: Улучшить алгоритм поиска с помощью анализа текста
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

    def del_from_search_list(self, key=None, drop=False):
        if drop:
            print('удаление уже известной десятки пользователей')
            for i in range(10):
                self.json_.pop(i)
        else:
            for page in self.json_:
                # print(page)
                try:
                    if page['personal'][key] == 5:
                        self.json_.remove(page)
                except KeyError:
                    continue

    def get_photos(self, user_list):
        results_json = []
        print('~ получаем фотографии')
        for usr in user_list:
            json_ = self.get_response(self.METHOD_PHOTOS_GET, {'owner_id': usr['id'],
                                                               'album_id': 'profile',
                                                               'extended': 1})

            new_list = sorted(json_['response']['items'], key=lambda x: x['likes']['count'], reverse=True)
            new_list = new_list[0:3]
            # print(new_list)
            photos = []
            for photo in new_list:
                photos.append({str(photo['id']): photo['sizes'][-1]['url']})
            results_json.append({'vk.com/id' + str(new_list[0]['owner_id']): photos})

        return results_json
        # print(json_['response']['items'])

    def likes_add(self):
        owner_id = int(input('Введите id пользователя - '))
        results.find_one_db(owner_id)
        print('Выберите фотографию:')
        item_id = int(input('Введите id фотографии - '))
        params = {'type': 'photo',
                  'owner_id': owner_id,
                  'item_id': item_id
                  }
        result = self.get_response(self.METHOD_LIKES_ADD, params)
        print(result)

    def likes_delete(self):
        owner_id = int(input('Введите id пользователя - '))
        print('Выберите фотографию:')
        results.find_one_db(owner_id)
        item_id = int(input('Введите id фотографии - '))
        params = {'type': 'photo',
                  'owner_id': owner_id,
                  'item_id': item_id
                  }
        result = self.get_response(self.METHOD_LIKES_DELETE, params)
        try:
            if result['error']:
                print('Вашего лайка нету на этой фотографии')
        except AttributeError:
            print(result)


def get_params_for_search():
    age = input('Введите диапазон возраста через - ').split('-')
    if age[0] > age[1]:
        print('Диапазон возраста введен неверно')
        sys.exit(0)
    gender = input('Введите пол - ').upper()
    searcher = VkSearcher(age=age, gender=gender)
    return age, gender, searcher


def runner():
    while True:
        cmd = input('Введите команду - ').lower()
        if cmd == 's' or cmd == 'search':
            age, gender, searcher = get_params_for_search()
            data = searcher.search()
            params = [searcher.user_info['id'], age, gender]
            results.post_data(params, data, searcher)
        elif cmd == 'al' or cmd == 'add like':
            liker = VkSearcher()
            liker.likes_add()
        elif cmd == 'dl' or cmd == 'delete like':
            liker = VkSearcher()
            liker.likes_delete()
        elif cmd == 'cl' or cmd == 'clear db':
            results.remove_db()
        elif cmd == 'p' or cmd == 'print':
            results.print_db()
        elif cmd == 'sf' or cmd == 'show favourites':
            results.show_favourites()
        elif cmd == 'af' or cmd == 'add favourites':
            user_id = input('Введите id пользователя - ')
            results.add_favourite(user_id)
        elif cmd == 'dff' or cmd == 'delete from favourites':
            user_id = input('Введите id пользователя - ')
            results.del_from_favourite(user_id)
        elif cmd == 'sb' or cmd == 'show blacklist':
            results.show_blacklist()
        elif cmd == 'aib' or cmd == 'add in blacklist':
            user_id = input('Введите id пользователя - ')
            results.add_in_blacklist(user_id)
        elif cmd == 'dfb' or cmd == 'delete from blacklist':
            user_id = input('Введите id пользователя - ')
            results.del_from_blacklist()
        elif cmd == 'e' or cmd == 'end':
            return
