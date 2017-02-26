#TODO header comments

import math

passed = []
values = []

class cClassifier():
    def __init__(self):
        self.gearClassifiers = [matchingRotation, gearAreaRatio, gearBetweenHeightRatio, minAreaDiff] #set the function names of classifiers to use here
        self.GEAR_SIGMAS = [50, 15, 1, 800] #Constants of where the sigmas start
        self.goalClassifiers = [matchingRotation, goalAreaRatio, goalBetweenHeightRatio] #set the function names of classifiers to use here
        self.GOAL_SIGMAS = [10, 1, 10] #Constants of where the sigmas start
    def classify(self, s1, s2, getVal, target): #returns true if it matches all of the classifiers, false if it fails any of them
        if target == "goal" or target == "turret":
            classifiers = self.goalClassifiers
            SIGMAS = self.GOAL_SIGMAS
        else:
            classifiers = self.gearClassifiers
            SIGMAS = self.GEAR_SIGMAS
        passFail = []
        for k, v in enumerate(classifiers):
            result, value = v(s1, s2, SIGMAS[k], getVal) #call the respective function
            print(str(v) + ' returned ' + str(result))
            print('with a value of ' + str(value))
            if not result:
                passFail.append(False)
                print('Not a ' + str(target))
                return False
                #print(passFail)
            passFail.append(True)
        print('Is a ' + str(target))
        return True
        
    def getValues(self):
        return(passed, values)

def matchingRotation(s1, s2, sigma, getVal):
    angleSigma = sigma
    result = s1[2] < s2[2] + angleSigma and s1[2] > s2[2] - angleSigma
    if not getVal:
        return (result, s1[2] - s2[2])
    else:
        return result
            
def distance(x1, y1, x2, y2):
    distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    if not distance == 0: return distance
    else: 
        print 'Distance is zero!'
        return -1
    
def goalAreaRatio(s1, s2, sigma, getVal):
    area1 = s1[1][0]*s1[1][1]
    area2 = s2[1][0]*s2[1][1]
    areaRatio = area1/area2
    areaSigma = sigma
    result = areaRatio < 1.5 + areaSigma and areaRatio > 1.5 - areaSigma
    if not getVal:
        return (result, areaRatio)
    else:
        return result
        
def goalBetweenHeightRatio(s1, s2, sigma, getVal):
    betweenHeightSigma = sigma
    centerDistance = distance(s1[0][0], s1[0][1], s2[0][0], s2[0][1])
    betweenHeightRatio = centerDistance - (0.5*(s2[1][1]+s1[1][1]))/s1[1][1]
    maxRatio = 30
    minRatio = 0.5
    result = betweenHeightRatio < maxRatio and betweenHeightRatio > minRatio
    if not getVal:
        return (result , betweenHeightRatio)
    else:
        return betweenHeightRatio
           
def minAreaDiff(s1, s2, sigma, getVal):
    area1 = s1[1][0]*s1[1][1]
    area2 = s2[1][0]*s2[1][1]
    if getVal: print 'Area diff: ' + str(area1 - area2)
    result = area1 - area2 < sigma and area1 - area2 > 0 - sigma
    return(result, area1 - area2)
    
def gearAreaRatio(s1, s2, sigma, getVal):
    area1 = s1[1][0]*s1[1][1]
    area2 = s2[1][0]*s2[1][1]
    areaRatio = area1/area2
    areaSigma = sigma
    result = areaRatio < 1 + areaSigma and areaRatio > 1 - areaSigma
    if not getVal:
        return (result, areaRatio)
    else:
        return areaRatio
 
def gearBetweenHeightRatio(s1, s2, sigma, getVal):
    centerDistance = distance(s1[0][0], s1[0][1], s2[0][0], s2[0][1])
    betweenHeightRatio = 0.5*(s2[1][1]+s1[1][1])/centerDistance
    maxRatio = 1
    minRatio = .1
    result = betweenHeightRatio < maxRatio and betweenHeightRatio > - maxRatio and (betweenHeightRatio > minRatio or betweenHeightRatio < - minRatio)
    return(result, betweenHeightRatio)
            
def centersToTopRatio(s1, s2, sigma, getVal):
    heightSigma = sigma
    centerDistance = distance(s1[0][0], s1[0][1], s2[0][0], s2[0][1])
    ratioToTop = centerDistance/s1[1][1]
    ratioToBottom = centerDistance/s2[1][1]
    if not getVal:
        return ratioToTop < 1.25 + heightSigma and ratioToTop > 1.25 - heightSigma
    else:
        return ratioToTop
