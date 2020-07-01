import pymongo
from pymongo import MongoClient
import psycopg2 as pg


client = MongoClient()
vkinder_results_db = client['vkinder_db']

def post_data(params, data):
    results = vkinder_results_db['results_vkinder']
    all_results = []
    for usr in data:
        user_items = list(usr.items())
        result = {'user_id': user_items[0][0],
                  'user_photos': user_items[0][1],
                  'params': params}
        # print(result)
        all_results.append(result)


    # results.insert_many(all_results)
    results.create_index([('user_id', pymongo.ASCENDING)], unique=True)


    print(list(results.find()))


