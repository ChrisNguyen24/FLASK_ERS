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

@app.route('/')
def index():
    cur = mysql.connection.cursor()
    items, ratings = load_data()
    print(ratings)
    print(items)

    return 'check loaded'

@app.route('/test')
def recommend():
    id = request.args.get('user_id')
    ratings = load_data()
    print(ratings)
    # result = list_predicts(str(id))
    return jsonify( {
        'data': id
} ), 201

def biparteMatrix(item_frame, ratings_frame):

    """
       convert the items data frame into userid-items biparte adjacency graph matrix

    """

    user_ids = list(ratings_frame.user_id.unique()) 
    movie_ids = list(item_frame.id.unique()) 

    numberOfUsers =  len(user_ids)

    numberOfMovies = len(movie_ids)
    
    
    
    # initialize a numpy matrix of of numberOfUsers * numberOfMovies

    user_movie_biparte = np.zeros((numberOfUsers, numberOfMovies))


    for name, group in ratings_frame.groupby(["userId", "movieId"]):

        #print name 
        #print group
        
        # name is a tuple (userId, movieId)
        
        userId, movieId = name

        user_index = user_ids.index(userId)
        movie_index = movie_ids.index(movieId)
        user_movie_biparte[user_index, movie_index] = group[["rating"]].values[0,0]

    return user_movie_biparte

def load_data():

    connection = mysql.connection
    # # Put it all to a data frame
    ratings = pd.read_sql_query ('''
                               SELECT
                               user_id, module_item_id, rating
                               FROM rs_comments
                               ''',connection)

    items = pd.read_sql_query ('''
                               SELECT
                               id, category_id, title
                               FROM rs_product
                               ''',connection)
     
    return items, ratings
    
