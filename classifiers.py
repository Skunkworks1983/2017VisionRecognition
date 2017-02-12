#TODO header comments

import math

class cClassifier():
    def __init__(self):
        self.gearClassifiers = [matchingRotation, gearAreaRatio, gearBetweenHeightRatio, minAreaDiff] #set the function names of classifiers to use here
        self.GEAR_SIGMAS = [50, 15, 1, 800] #Constants of where the sigmas start
        self.goalClassifiers = [matchingRotation, goalAreaRatio, goalBetweenHeightRatio] #set the function names of classifiers to use here
        self.GOAL_SIGMAS = [10, 1, 10] #Constants of where the sigmas start
    def classify(self, s1, s2, DEBUG, target): #returns true if it matches all of the classifiers, false if it fails any of them
        if target == "goal" or target == "turret":
            classifiers = self.goalClassifiers
            SIGMAS = self.GOAL_SIGMAS
        else:
            classifiers = self.gearClassifiers
            SIGMAS = self.GEAR_SIGMAS
        passFail = []
        #if not DEBUG:
        if True: #What even is this?
            for k, v in enumerate(classifiers):
                if not v(s1, s2, SIGMAS[k], False): #call the respective function
                    passFail.append(False)
                    return False
                    #print(passFail)
                passFail.append(True)
            return True
        else:
            values = []
            for k, v in enumerate(classifiers):
                values.append(v(s1, s2, SIGMAS[k], True))
            return values

def matchingRotation(s1, s2, sigma, getVal):
    angleSigma = sigma
    if not getVal:
        return s1[2] < s2[2] + angleSigma and s1[2] > s2[2] - angleSigma
    else:
        return s1[2]/(s2[2] + .001)
            
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
    if not getVal:
        return areaRatio < 1.5 + areaSigma and areaRatio > 1.5 - areaSigma
    else:
        return areaRatio
        
def goalBetweenHeightRatio(s1, s2, sigma, getVal):
    betweenHeightSigma = sigma
    centerDistance = distance(s1[0][0], s1[0][1], s2[0][0], s2[0][1])
    betweenHeightRatio = centerDistance - (0.5*(s2[1][1]+s1[1][1]))/s1[1][1]
    maxRatio = 30
    minRatio = 0.5
    if not getVal:
        return betweenHeightRatio < maxRatio and betweenHeightRatio > minRatio
    else:
        return betweenHeightRatio
           
def minAreaDiff(s1, s2, sigma, getVal):
    area1 = s1[1][0]*s1[1][1]
    area2 = s2[1][0]*s2[1][1]
    if DEBUG: print 'Area diff: ' + str(area1 - area2)
    return area1 - area2 < sigma and area1 - area2 > 0 - sigma
    
def gearAreaRatio(s1, s2, sigma, getVal):
    area1 = s1[1][0]*s1[1][1]
    area2 = s2[1][0]*s2[1][1]
    areaRatio = area1/area2
    areaSigma = sigma
    if not getVal:
        return areaRatio < 1 + areaSigma and areaRatio > 1 - areaSigma
    else:
        return areaRatio
 
def gearBetweenHeightRatio(s1, s2, sigma, getVal):
    centerDistance = distance(s1[0][0], s1[0][1], s2[0][0], s2[0][1])
    betweenHeightRatio = 0.5*(s2[1][1]+s1[1][1])/centerDistance
    maxRatio = 1
    minRatio = .1
    if DEBUG: print 'Height ratio: ' + str(betweenHeightRatio)
    if betweenHeightRatio < maxRatio and betweenHeightRatio > - maxRatio and (betweenHeightRatio > minRatio or betweenHeightRatio < - minRatio):
        
        return True
    else:
        return False
            
def centersToTopRatio(s1, s2, sigma, getVal):
    heightSigma = sigma
    centerDistance = distance(s1[0][0], s1[0][1], s2[0][0], s2[0][1])
    ratioToTop = centerDistance/s1[1][1]
    ratioToBottom = centerDistance/s2[1][1]
    if not getVal:
        return ratioToTop < 1.25 + heightSigma and ratioToTop > 1.25 - heightSigma
    else:
        return ratioToTop
