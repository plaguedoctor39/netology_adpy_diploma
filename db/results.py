import pymongo
from pymongo import MongoClient
from vk_api import vk_search
import psycopg2 as pg

client = MongoClient()
vkinder_results_db = client['vkinder_db']


def post_data(params, data, searcher):
    results = vkinder_results_db['results_vkinder']
    all_results = []
    for usr in data:
        user_items = list(usr.items())
        result = {'user_id': user_items[0][0],
                  'user_photos': user_items[0][1],
                  'params': params}
        if len(list(results.find({'user_id': user_items[0][0]}))) == 0:
            print('Добавляем пользователя в список')
            all_results.append(result)
        # print(result)

    if len(all_results) != 0:
        print('Добавляем пользователей в бд')
        results.insert_many(all_results)
    else:
        print('Получаем следующие 10 результатов')
        new_data = searcher.search(next10=True)
        post_data(params, new_data, searcher)
    # results.create_index([('user_id', pymongo.ASCENDING)], unique=True)
    # print(results.index_information())

    print(list(results.find()))


def add_favourite(user_id):
    results = vkinder_results_db['results_vkinder']
    favourites = vkinder_results_db['favourites_vkinder']
    if len(list(results.find({'user_id': 'vk.com/id' + str(user_id)}))) == 0:
        print('Такого пользователя нету в бд')
        return
    if len(list(favourites.find({'user_id': user_id}))) != 0:
        print('Такой пользователь уже есть в избранных')
        return
    else:
        favourites.insert({'user_id': user_id})
        print(list(favourites.find()))


def del_from_favourite(user_id):
    favourites = vkinder_results_db['favourites_vkinder']
    if len(list(favourites.find({'user_id': user_id}))) != 0:
        favourites.remove({'user_id': user_id})
        print('Пользователь успешно удален из избранных')
    else:
        print('Пользователя нету в бд')


def add_in_blacklist(user_id):
    results = vkinder_results_db['results_vkinder']
    blacklist = vkinder_results_db['blacklist_vkinder']
    if len(list(results.find({'user_id': 'vk.com/id' + str(user_id)}))) == 0:
        print('Такого пользователя нету в бд')
        return
    if len(list(blacklist.find({'user_id': user_id}))) == 0:
        blacklist.insert({'user_id': user_id})
        print('Пользователь успешно добавлен в черный список')
    else:
        print('Пользователь уже есть в черном списке')


def del_from_blacklist(user_id):
    blacklist = vkinder_results_db['blacklist_vkinder']
    if len(list(blacklist.find({'user_id': user_id}))) != 0:
        blacklist.remove({'user_id': user_id})
        print('Пользователь успешно удален из черного списка')
    else:
        print('Пользователя нету в бд')

def check_blacklist(user_id):
    blacklist = vkinder_results_db['blacklist_vkinder']
    if len(list(blacklist.find({'user_id': user_id}))) != 0:
        return 1
    else:
        return 0