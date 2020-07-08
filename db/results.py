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
