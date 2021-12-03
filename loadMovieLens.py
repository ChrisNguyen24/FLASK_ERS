import sys
import os

def loadMovieLensTrain(fileName='u1.base'):
    #str1 = './ml-100k/'
    
    prefer = {}
    for line in open(fileName,'r'):     
        (userid, movieid, rating,ts) = line.split('\t')
        u = int(userid)
        i = int(movieid)
        prefer.setdefault(u, {})
        prefer[u][i] = float(rating)    

    return prefer

def loadMovieLensTest(fileName='u1.test'):
    #str1 = './ml-100k/'
    prefer = {}
    for line in open(fileName,'r'):
        (userid, movieid, rating,ts) = line.split('\t')
        u = int(userid)
        i = int(movieid)
        prefer.setdefault(u, {})    
        prefer[u][i] = float(rating)   
    return prefer                   


if __name__ == "__main__":
    print ("""load train/test dataset..""")
    
    trainDict = loadMovieLensTrain()
    testDict = loadMovieLensTest()

    print (len(trainDict))
    print (len(testDict))
    print (""" load train/test dataset complete """)
                        

















