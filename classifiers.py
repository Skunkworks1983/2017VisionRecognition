import math

class cClassifier():
    def __init__(self):
        self.classifiers = [matchingRotation, areaRatio, centersToTopRatio, betweenHeightRatio] #set the function names of classifiers to use here
        self.SIGMAS = [15, 0.75, 1, 0.3] #Constants of where the sigmas start #I get that these numbers corrolate to the function names above them,
                                         #it took me a few seconds, it would be nice if it was just explicitly stated above 
    def classify(self, s1, s2): #returns true if it matches all of the classifiers, false if it fails any of them
        passFail = []
        for k, v in enumerate(self.classifiers):
            if not v(s1, s2, self.SIGMAS[k]): #call the respective function
                passFail.append(False)
                return False
            passFail.append(True)
        return True

def distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

def areaRatio(s1, s2, sigma):
    area1 = s1[1][0]*s1[1][1]
    area2 = s2[1][0]*s2[1][1]
    areaRatio = area1/area2
    areaSigma = sigma #simpler if you did this in function decleration
    return areaRatio < 1.5 + areaSigma and areaRatio > 1.5 - areaSigma #magic numbers
    
def centersToTopRatio(s1, s2, sigma):
    heightSigma = sigma #simpler if you did this in function decleration
    centerDistance = distance(s1[0][0], s1[0][1], s2[0][0], s2[0][1])
    ratioToTop = centerDistance/s1[1][1]
    ratioToBottom = centerDistance/s2[1][1]
    return ratioToTop < 1.25 + heightSigma and ratioToTop > 1.25 - heightSigma #magic numbers

def matchingRotation(s1, s2, sigma):
    angleSigma = sigma
    return s1[2] < s2[2] + angleSigma and s1[2] > s2[2] - angleSigma

def betweenHeightRatio(s1, s2, sigma):
    betweenHeightSigma = sigma
    centerDistance = distance(s1[0][0], s1[0][1], s2[0][0], s2[0][1])
    betweenHeightRatio = centerDistance - (0.5*(s2[1][1]+s1[1][1]))/s1[1][1]
    maxRatio = 50
    minRatio = 20
    return betweenHeightRatio < maxRatio and betweenHeightRatio > minRatio
