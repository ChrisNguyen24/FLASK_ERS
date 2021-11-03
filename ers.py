import math
import numpy as np
from sklearn.model_selection import train_test_split
import pandas as pd
dataset = []
uu_dataset = {}
ii_dataset = {}
@app.route('/recommendations')
def recommend():
    id = request.args.get('customer')
    load_data()
    result = list_predicts(str(id))
    return jsonify( {
        'data': result
} ), 201

def pearson_correlation(user1, user2): #tương quan person
    result = 0.0
    global uu_dataset
    if (user1 in uu_dataset.keys() and user2 in uu_dataset.keys()):
        user1_data = uu_dataset[user1]
        user2_data = uu_dataset[user2]
        rx_avg = user_average_rating(user1_data)
        ry_avg = user_average_rating(user2_data)
        sxy = common_items(user1_data, user2_data)
        top_result = 0.0
        bottom_left_result = 0.0
        bottom_right_result = 0.0
        for item in sxy:
            rxs = user1_data[item]
            rys = user2_data[item]
            top_result += (rxs - rx_avg)*(rys - ry_avg)
            bottom_left_result += pow((rxs - rx_avg), 2)
            bottom_right_result += pow((rys - ry_avg), 2)
        bottom_left_result = math.sqrt(bottom_left_result)
        bottom_right_result = math.sqrt(bottom_right_result)
        if top_result != 0:
            result = top_result/(bottom_left_result * bottom_right_result)
    return result
    
def user_average_rating(user_data): # trung bình đánh giá
    avg_rating = 0.0
    size = len(user_data)
    for (item, rating) in user_data.items():
        avg_rating += float(rating)
    avg_rating /= size * 1.0
    return avg_rating

def common_items(user1_data, user2_data): # get các item chung của 2 user
    result = []
    ht = {}
    for (item, rating) in user1_data.items():
        ht.setdefault(item, 0)
        ht[item] += 1
    for (item, rating) in user2_data.items():
        ht.setdefault(item, 0)
        ht[item] += 1
    for (k, v) in ht.items():
        if v == 2:
            result.append(k)
    return result

def k_nearest_neighbors(user, k, item_id): # get k láng giềng gần nhất
    neighbors = []
    result = []
    global ii_dataset, uu_dataset
    if item_id in ii_dataset.keys():
        users_rating_item = ii_dataset[item_id].keys()
        for (user_id, data) in uu_dataset.items():
            if user_id in users_rating_item:
                upc = pearson_correlation(user, user_id)
                neighbors.append([user_id, upc])
        sorted_neighbors = sorted(neighbors, key=lambda neighbors: (neighbors[1], neighbors[0]), reverse=True)
        for i in range(k):
            if i >= len(sorted_neighbors):
                break
        result.append(sorted_neighbors[i])
    return result

def list_predicts(user_id): #get các item được dự đoán
    items_predict = {}
    global uu_dataset, ii_dataset
    for (item, data) in ii_dataset.items():
        if item not in uu_dataset[user_id]:
            kNearestNeighbors = k_nearest_neighbors(user_id, 25, str(item))
            rate_predict = predict(user_id, item, kNearestNeighbors)
            items_predict.setdefault(item, rate_predict)
    items_predict2 = sorted(items_predict.items(), key=lambda items_predict:(items_predict[1], items_predict[0]), reverse=True)
    keys = []
    for (key, data) in items_predict2:
        keys.append(int(key))
    if len(items_predict2) > 7:
        result = keys[0:7]
    else:
        result = key
    return result

def predict(user, item, k_nearest_neighbors): #tính toán các rating còn thiếu
    result = 0.0
    global uu_dataset
    if user in uu_dataset.keys():
        valid_neighbors = k_nearest_neighbors
        userAverageRating = user_average_rating(uu_dataset[user])
        if not len(valid_neighbors):
            return userAverageRating
        top_result = 0.0
        bottom_result = 0.0
        for neighbor in valid_neighbors:
            neighbor_id = neighbor[0]
            neighbor_similarity = neighbor[1]
            user_neighbor_data = uu_dataset[neighbor_id]
            avg_neighbor = user_average_rating(user_neighbor_data)
            rating = uu_dataset[neighbor_id][item]
            top_result += neighbor_similarity * (rating - avg_neighbor)
            bottom_result += abs(neighbor_similarity)
        if bottom_result == 0:
            return userAverageRating
        user_data = uu_dataset[user]
        avg = user_average_rating(user_data)
        result = avg + (top_result/bottom_result)
    return result

def load_data():
    global dataset, uu_dataset, ii_dataset
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM rates')
    rates = cur.fetchall()
    dataset = []
    for rate in rates:
        dataset.append([
            str(rate[4]),
            str(rate[3]),
            str(rate[1])
        ])
        uu_dataset.setdefault(str(rate[4]), {})
        uu_dataset[str(rate[4])].setdefault(str(rate[3]), float(str(rate[1])))
        ii_dataset.setdefault(str(rate[3]), {})
        ii_dataset[str(rate[3])].setdefault(str(rate[4]), float(str(rate[1])))
