from flask import Flask , render_template, request, jsonify
from flask_mysqldb import MySQL
import pandas as pd
import numpy as np
import math

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'ecommerce'
mysql = MySQL(app)

dataset = []
uu_dataset = {}
ii_dataset = {}

# @app.route('/')
# def index():
#     cur = mysql.connection.cursor()
#     ratings = load_data()
    
#     print(ratings)
#     return 'check loaded'

@app.route('/test')
def recommend():
    id = request.args.get('user_id')
    ratings = load_data()
    print(ratings)
    # user_ids = list(ratings.user_id.unique()) 
    # item_ids = list(ratings.module_item_id.unique()) 
    # numberOfUsers =  len(user_ids)
    # numberOfItem = len(item_ids)

    w, wt, uz, pz = biparteMatrix(ratings)
    z = graphWeightMatrix(w, wt, uz, pz)
    print(w[0][0])
    print(w)
    print(z)
    
    # result = list_predicts(str(id))
    return jsonify( {
        'data': id
} ), 201

def biparteMatrix(ratings_frame):

    """
       convert the ratings frame into userid-items biparte adjacency graph matrix

    """
    ratings_frame.rating = ratings_frame.rating.astype('float64')

    user_ids = list(ratings_frame.user_id.unique()) 
    item_ids = list(ratings_frame.module_item_id.unique()) 
    numberOfUsers =  len(user_ids)
    numberOfItem = len(item_ids)
    
    # initialize a numpy matrix of of numberOfUsers * numberOfItem
    w_biparte = np.zeros((numberOfUsers, numberOfItem))

    for name, group in ratings_frame.groupby(["user_id", "module_item_id"]):
        userId, itemId = name
        user_index = user_ids.index(userId)
        items_index = item_ids.index(itemId)

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
    print(L)
    print(uz_L)
    return L, uz_L

# Item based
def similarityBasedItem(w, wt):
    L = 2
    pz_L = np.dot(wt,w)
    while 0 in pz_L:
        L += 2
        tmp = np.dot(wt,w)
        pz_L = np.dot(tmp, pz_L)
    print(L)
    print(pz_L)
    return L, pz_L

# kNN user based
def k_nn(U, user_id, k):
    neighbors = []
    result = []
    for index, u in enumerate(U[user_id]):
      if index == user_id : continue
      neighbors.append([index, u])
    sorted_neighbors = sorted(neighbors, key=lambda neighbors: (neighbors[1], neighbors[0]), reverse=True)
    print(sorted_neighbors)
    for i in range(k):
      if i >= len(sorted_neighbors):
        break
      result.append(sorted_neighbors[i][0])
    
    return result

