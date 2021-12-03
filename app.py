from flask import Flask , render_template, request, jsonify
from flask_mysqldb import MySQL
import pandas as pd
import numpy as np
import math
import json

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'ecommerce'
mysql = MySQL(app)

w_biparte = []
user_dataset = []
item_dataset = []

# @app.route('/')
# def index():


@app.route('/cf-recommender')
def recommend():
    global user_dataset, item_dataset, w_biparte
    rs = []
    user_id = request.args.get('user_id')
    ratings = load_data()
    msg = 'got list recommendation'

    w_biparte, wt, uz, pz = biparteMatrix(ratings)
    # z = graphWeightMatrix(w, wt, uz, pz)  
    # print(w_biparte)
    # print(item_dataset)
    # print(user_dataset)
    try:
        user_index = user_dataset.index(int(user_id))
        # print(user_index)
        
        index_result = list_predicts(w_biparte, user_index)

        for i in index_result:
            rs_item = int(item_dataset[i])
            rs.append(rs_item)
            
    except:
        print("Not has user_id")
        msg = "User has not data rating"
        
    return jsonify({
            'msg': msg,
            'data': rs,
            'user_id' : user_id
            },200)
    

        

def biparteMatrix(ratings_frame):

    """
       convert the ratings frame into userid-items biparte adjacency graph matrix

    """
    global user_dataset, item_dataset, w_biparte
    
    ratings_frame.rating = ratings_frame.rating.astype('float64')

    user_ids = list(ratings_frame.user_id.unique()) 
    item_ids = list(ratings_frame.module_item_id.unique()) 
    numberOfUsers =  len(user_ids)
    numberOfItem = len(item_ids)

    user_dataset = user_ids
    item_dataset = item_ids

    # print(user_ids)
    # print('***********')
    # print(item_ids)
    
    # initialize a numpy matrix of of numberOfUsers * numberOfItem
    w_biparte = np.zeros((numberOfUsers, numberOfItem))

    for name, group in ratings_frame.groupby(["user_id", "module_item_id"]):
        userId, itemId = name
        user_index = user_ids.index(userId)
        items_index = item_ids.index(itemId)
        # print('--------')
        # print(user_index, items_index, group[["rating"]].values[0,0])
        
        w_biparte[user_index, items_index] = group[["rating"]].values[0,0]/5

    # initialize uz pz
    uz = np.zeros((numberOfUsers, numberOfUsers))
    pz = np.zeros((numberOfItem, numberOfItem))

    return w_biparte, w_biparte.T, uz, pz

def graphWeightMatrix(w, wt, uz, pz):
    uzw = np.concatenate((uz, wt), axis=0)
    wpz = np.concatenate((w, pz), axis=0)
    # print(uzw)
    # print('\n',wpz)
    z = np.concatenate((uzw, wpz), axis = 1)
    # print(z)
    return z

def load_data():

    connection = mysql.connection
    # # Put it all to a data frame
    ratings = pd.read_sql_query ('''
                               SELECT
                               user_id, module_item_id, rating
                               FROM rs_comments
                               ''',connection)

    # items = pd.read_sql_query ('''
    #                            SELECT
    #                            id, category_id, title
    #                            FROM rs_product
    #                            ''',connection)
     
    return ratings
    
def similarityBasedUser(w, wt):
    L = 2
    uz_L = np.dot(w, wt)
    while 0 in uz_L:
        L += 2
        tmp = np.dot(w, wt)
        uz_L = np.dot(tmp, uz_L)
    # print(L)
    # print(uz_L)
    return L, uz_L

# Item based
def similarityBasedItem(w, wt):
    L = 2
    pz_L = np.dot(wt,w)
    while 0 in pz_L:
        L += 2
        tmp = np.dot(wt,w)
        pz_L = np.dot(tmp, pz_L)
    # print(L)
    # print(pz_L)
    return L, pz_L

# kNN user based
def k_nn(U, user_id, k):
    neighbors = []
    result = []
    for index, u in enumerate(U[user_id]):
        if index == user_id : continue
        neighbors.append([index, u])
    sorted_neighbors = sorted(neighbors, key=lambda neighbors: (neighbors[1], neighbors[0]), reverse=True)
    # print(sorted_neighbors)
    for i in range(k):
        if i >= len(sorted_neighbors):
            break
        result.append(sorted_neighbors[i][0])
    
    return result

def predict(user_id, Knn):
    result = []
    for index, rating in enumerate(w_biparte[user_id]):
        if rating == 0 :
            avg_rating = user_average_rating(Knn, index)
            # W[user_id][index] = avg_rating
            result.append([index, avg_rating])

    return result

def user_average_rating(Knn, item_id): 
    global w_biparte
    avg_rating = 0.0
    size = len(Knn)
    for u in Knn:
        avg_rating += float(w_biparte[u][item_id])
    avg_rating /= size * 1.0
    return avg_rating

def list_predicts(w, user_id, q = 5, k = 3):
    result = []
    wt = w.T
    L, Ul = similarityBasedUser(w, wt)
    knn = k_nn(Ul, user_id, k)
    # fill rating predict for user_id
    list_predict = predict(user_id, knn)

    sorted_predict = sorted(list_predict, key=lambda list_predict: (list_predict[1]), reverse=True)
    for i in range(min(q,len(sorted_predict))):
        if i > q : break
        result.append(sorted_predict[i][0])
    return result
