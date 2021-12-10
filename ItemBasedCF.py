import math, datetime
from math import sqrt
from loadMovieLens import loadMovieLensTrain
from loadMovieLens import loadMovieLensTest

class ItemBasedCF:
    def __init__(self):
        pass

def sim_pearson(prefer, item1, item2):
    sim={}

    #common users of item1 & item2
    for user in prefer[item1]:
        if user in prefer[item2]:
            sim[user] = 1

    n=len(sim)
    if len(sim)==0:
        return -1

    sum1=sum([prefer[item1][user] for user in sim])
    sum2=sum([prefer[item2][user] for user in sim])

    sum1Sq = sum([pow(prefer[item1][user], 2) for user in sim])
    sum2Sq = sum([pow(prefer[item2][user], 2) for user in sim])

    sumMulti = sum([prefer[item1][user] * prefer[item2][user] for user in sim])

    num1 = sumMulti - (sum1 * sum2 / n)
    num2 = sqrt((sum1Sq - pow(sum1, 2) / n) * (sum2Sq - pow(sum2, 2) / n))
    if num2 == 0: 
        return 0

    result = num1 / num2
    return result

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

def topKMatches(prefer, itemId, userId, k=20, sim=sim_pearson):
    itemSet = []
    scores = []
    items = []

    #item has also been rated by user
    for item in prefer:
        if userId in prefer[item]:
            itemSet.append(item)

    #list [(score, item),..]
    scores = [(sim(prefer, itemId, other), other) for other in itemSet if other != itemId]

    scores.sort()
    scores.reverse()

    if len(scores) <= k: 
        for item in scores:
            items.append(item[1])  
        return items
    else:  
        kscore = scores[0:k]
        for item in kscore:
            items.append(item[1])  
        return items  

def getAverage(prefer, itemId):
    count = 0
    sum = 0
    for user in prefer[itemId]:
        sum += prefer[itemId][user]
        count += 1
    return sum / count

def getRating(prefer1, userId, itemId, knumber=20, similarity=sim_pearson):
    sim = 0.0
    averageOther = 0.0
    toAverage = 0.0
    simSums = 0.0

    items = topKMatches(prefer1, itemId, userId, k=knumber, sim=similarity)

    averageOfItem = getAverage(prefer1, itemId)

    for other in items:
        sim = similarity(prefer1, itemId, other) 
        averageOther = getAverage(prefer1, other) 

        simSums += abs(sim)  
        toAverage += (prefer1[other][userId] - averageOther) * sim  

    if simSums == 0:
        return averageOfItem
    else:
        return (averageOfItem + toAverage / simSums)

#Evaluation
def getRMSE(records):
    return math.sqrt(sum([(rui-pui)*(rui-pui) for u,i,rui,pui in records])/float(len(records)))

def getMAE(records):
    return sum([abs(rui-pui) for u,i,rui,pui in records])/float(len(records))

#==================================================================
def getAllUserRating(fileTrain='u1.base', fileTest='u1.test',k=20, sim = sim_pearson):
    traindata = loadMovieLensTrain(fileTrain)
    testdata = loadMovieLensTest(fileTest)  
    
    # print('building movie-users inverse table...')
    movie2users = {}
    for user, movies in traindata.items():
        for movie, rating in movies.items():
            movie2users.setdefault(movie, {})
            movie2users[movie][user] = float(rating)

    inAllnum = 0
    records=[]
    for userid in testdata: 
        for item in testdata[userid]:
            if item in movie2users:
                rating = getRating(movie2users, userid, item, k, similarity=sim) 
                records.append([userid,item,testdata[userid][item],rating])
    #         inAllnum = inAllnum + 1
    # print("-------------Completed!!-----------", inAllnum)
    return records

if __name__ == "__main__":
    testfile='Data/ml-100k/u1.test'
    trainfile='Data/ml-100k/u1.base'
    print("\n--------------Itembased - cosine... -----------\n")
    print("%3s%20s%20s%20s" % ('K', "RMSE","MAE", "Time(s)"))
    for k in [5, 10, 20, 40, 80, 160]:
        starttime = datetime.datetime.now()
        r=getAllUserRating(trainfile, testfile, k, sim_cosine)
        rmse=getRMSE(r)
        mae=getMAE(r)
        print("%3d%19.3f%19.3f%17ss" % (k, rmse, mae, (datetime.datetime.now() - starttime).seconds))

    print("\n--------------Itembased - pearson... -----------\n")
    print("%3s%20s%20s%20s" % ('K', "RMSE","MAE", "Time(s)"))
    for k in [5, 10, 20, 40, 80, 160]:
        starttime = datetime.datetime.now()
        r=getAllUserRating(trainfile, testfile, k)
        rmse=getRMSE(r)
        mae=getMAE(r)
        print("%3d%19.3f%19.3f%17ss" % (k, rmse, mae, (datetime.datetime.now() - starttime).seconds))
