import math, random, sys, datetime
from math import sqrt
from loadMovieLens import loadMovieLensTrain
from loadMovieLens import loadMovieLensTest
import pickle
import os
from operator import itemgetter

class UserBasedCF:
    def __init__(self):
        pass

def sim_pearson(prefer, person1, person2):
    sim = {}
    #common items of user1 & user2
    for item in prefer[person1]:
        if item in prefer[person2]:
            sim[item] = 1  

    n = len(sim)
    if len(sim) == 0:
        return -1

    sum1 = sum([prefer[person1][item] for item in sim])
    sum2 = sum([prefer[person2][item] for item in sim])

    sum1Sq = sum([pow(prefer[person1][item], 2) for item in sim])
    sum2Sq = sum([pow(prefer[person2][item], 2) for item in sim])

    sumMulti = sum([prefer[person1][item] * prefer[person2][item] for item in sim])

    num1 = sumMulti - (sum1 * sum2 / n)
    num2 = sqrt((sum1Sq - pow(sum1, 2) / n) * (sum2Sq - pow(sum2, 2) / n))
    if num2 == 0:
        return 0

    result = num1 / num2
    return result

def topKMatches(prefer, person, itemId, k=20, sim=sim_pearson):
    userSet = []
    scores = []
    users = []
   
    #user has also rated by item
    for user in prefer:
        if itemId in prefer[user]:
            userSet.append(user)
            
    #list [(score, user),..]
    scores = [(sim(prefer, person, other), other) for other in userSet if other != person]

    scores.sort()
    scores.reverse()

    if len(scores) <= k:
        for item in scores:
            users.append(item[1])
        return users
    else:
        kscore = scores[0:k]
        for item in kscore:
            users.append(item[1])
        return users

def getAverage(prefer, userId):
    count = 0
    sum = 0
    for item in prefer[userId]:
        sum += prefer[userId][item]
        count += 1
    return sum / count
    
def sim_cosine(prefer, person1, person2):
    sim = {}
    # common items of user1 & user2
    for item in prefer[person1]:
        if item in prefer[person2]:
            sim[item] = 1

    n = len(sim)
    if len(sim) == 0:
        return -1

    sum1Sq = sum([pow(prefer[person1][item], 2) for item in sim])
    sum2Sq = sum([pow(prefer[person2][item], 2) for item in sim])

    sumMulti = sum([prefer[person1][item] * prefer[person2][item] for item in sim])

    num1 = sumMulti
    num2 = sqrt(sum1Sq) * sqrt(sum2Sq)
    if num2 == 0:
        return 0

    result = num1 / num2
    return result


def getRating(prefer1, userId, itemId, knumber=20, similarity=sim_pearson):
    sim = 0.0
    averageOther = 0.0
    toAverage = 0.0
    simSums = 0.0

    knnUsers = topKMatches(prefer1, userId, itemId, k=knumber, sim=sim_pearson)

    averageOfUser = getAverage(prefer1, userId)
    for other in knnUsers:
        sim = similarity(prefer1, userId, other) 
        averageOther = getAverage(prefer1, other)

        simSums += abs(sim)
        toAverage += (prefer1[other][itemId] - averageOther) * sim  

    if simSums == 0:
        return averageOfUser
    else:
        return (averageOfUser + toAverage / simSums)

#==================================================================
def getAllUserRating(fileTrain='u1.base', fileTest='u1.test',k=20):
    traindata = loadMovieLensTrain(fileTrain)
    testdata = loadMovieLensTest(fileTest)
    # print('size trainset', len(traindata))
    # print('size testset', len(testdata))
    inAllnum = 0
    records=[]
    for userid in testdata:
        for item in testdata[userid]:
            rating = getRating(traindata, userid, item, k, sim_cosine)
            records.append([userid,item,testdata[userid][item],rating])
    #         inAllnum = inAllnum + 1
    # print("-------------Completed!!-----------", inAllnum)
    return records

#Evaluation
def getRMSE(records):
    return math.sqrt(sum([(rui-pui)*(rui-pui) for u,i,rui,pui in records]))/float(len(records))

def getMAE(records):
    return sum([abs(rui-pui) for u,i,rui,pui in records])/float(len(records))

def recallAndPrecision( train=None, test=None, k=8, nitem=10):
    hit = 0
    recall = 0
    precision = 0
    for user in train.keys():
        tu = test.get(user, {})
        rank = recommender(train, user, k, nitem)
        for item in rank:
            if item in tu:
                hit += 1
        recall += len(tu)
        precision += nitem
    return (hit / (recall * 1.0), hit / (precision * 1.0))

####
def calculate_user_similarity(dataset):
    # print('building item-users inverse table...')
    usersim_mat = {}
    item2users = {}
    for user, items in dataset.items():
        for item, rating in items.items():
            item2users.setdefault(item, {})
            item2users[item][user] = float(rating)

    for i, u in item2users.items():
        for u1 in u:
            usersim_mat.setdefault(u1,{})
            for u2 in u:
                if u1 == u2:
                    continue
                usersim_mat[u1][u2] = sim_pearson(dataset, u1, u2)

    return usersim_mat  

def save_model(model, save_name: str):
    if 'pkl' not in save_name:
        save_name += '.pkl'
    if not os.path.exists('model'):
        os.mkdir('model')
    pickle.dump(model, open('model/' + "%s" % save_name, "wb"))

def load_model(model_name: str):
    if 'pkl' not in model_name:
        model_name += '.pkl'
    if not os.path.exists('model' + "-%s" % model_name):
        raise OSError('There is no model named %s in model/ dir' % model_name)
    return pickle.load(open('model/' + "%s" % model_name, "rb"))

def recommender(dataset, user, k = 10, n = 10):
    predict = {}
    seen_items = dataset.get(user, {})
    user_sim = load_model('user_sim')
    for sim_user, sim_score in list(sorted(user_sim[user].items(), key=itemgetter(1), reverse=True))[0:k]:
        for item, rating in dataset[sim_user].items():
            if item in seen_items:
                continue
            predict.setdefault(item,{})
            predict[item] = getRating(dataset, sim_user, item, k)

    return [movie for movie, _ in sorted(predict.items(), key=itemgetter(1), reverse=True)[0:n]]

if __name__ == "__main__":
    trainfile = 'Data/ml-100k/u1.base'
    testfile = 'Data/ml-100k/u1.test'

    print("\n--------------Dataset from MovieLens... -----------\n")
    print("%3s%20s%20s%20s" % ('K', "RMSE","MAE","Time(s)"))
    for k in [ 5, 10, 20, 40, 80, 160]:
    #     recall, precision = recallAndPrecision(loadMovieLensTrain(trainfile), loadMovieLensTest(testfile), k)
    #     print(k,': ',recall, precision)
        starttime = datetime.datetime.now()
        r=getAllUserRating(trainfile,testfile , k)
        rmse=getRMSE(r)
        mae=getMAE(r)
        print("%3d%19.3f%%%19.3f%%%17ss" % (k, rmse * 100, mae * 100, (datetime.datetime.now() - starttime).seconds))


    #########################
    # dataset = loadMovieLensTrain(trainfile)
    # # user_sim = calculate_user_similarity(dataset)
    # # save_model(user_sim, 'user_sim')

    # rec = recommender(dataset,1)
    # print(rec)
    # recall, precision = recallAndPrecision(loadMovieLensTrain(trainfile), loadMovieLensTest(testfile), 80)
    # print(recall, precision)
    # print('done')