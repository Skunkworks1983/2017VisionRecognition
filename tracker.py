from cShapeDetector import cShapeDetector
import numpy as np
import cv2, time, sys, math

np.set_printoptions(threshold=np.nan)

def loadCapture(filename): 
    return cv2.VideoCapture(filename) 
    
def distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    
fileName = "./testPhotos/test1.h264"
cap = loadCapture(fileName)

millis = int(round(time.time() * 1000)) #Initialize time
pauseFR = False

def doNothing(val): #necesasry for the return of createTrackbar
    pass

t_val = 60
shapes = 2
imageNum = 0
cv2.namedWindow("trackbar", cv2.WINDOW_NORMAL)
cv2.createTrackbar("t_val", "trackbar", t_val, 255, doNothing) #Creates a trackbar on the window "trackbar" to adjust t_val (threshold)
cv2.createTrackbar("shapes", "trackbar", shapes, 100, doNothing) #Creates a trackbar on the window "trackbar" to adjust shapes (total recs found)

frameCount = 0.1 #float so that we get float division
foundFrames = 0

while(True):
    frameCount += 1
    # Capture frame-by-frame
    if not cap.grab(): #if the video has run out of frames
        print("Not cap grab")
        print("Percentage found: " + str(foundFrames/frameCount))
        cap = loadCapture(fileName) #reload the video and start again
        cap.grab() 
    ret, frame = cap.retrieve()
    
    saved = frame.copy() #to save the image if spacebar was pressed
    
    t_val = cv2.getTrackbarPos("t_val", "trackbar")       #Update the image and trackbar positions
    shapes = cv2.getTrackbarPos("shapes", "trackbar")

    # Our operations on the frame come here
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) #Convert to gray, and then threshold based on t_val
    maxThresh = 255
    ret, thresholded = cv2.threshold(gray, t_val, maxThresh ,cv2.THRESH_BINARY)
    
    #thresholded = np.uint8(np.clip(gray, np.percentile(gray, t_val), 100))
    cv2.imshow("thresholded", thresholded)

    contour_img, contours, hierarchy = cv2.findContours(thresholded, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE) #Find the contours on the thresholded image
    
    contours.sort(key = lambda s: -1 * len(s)) #Sort the list of contours by the length of each contour (smallest to biggest)
    
    thresholded = cv2.cvtColor(thresholded, cv2.COLOR_GRAY2BGR) #turn it back to BGR so that when we draw things they show up in BGR
    
    displayed = frame
    #print(larger)
    #print(contours)
    shapeContours = []
    
    #TESTING
    '''try:
        print("Set contour to last")
        contours = contours[-1]
    except:
        print("But actually didn't")
        contours = []'''
        
    
    
    for s1 in contours:
        s1box = cv2.minAreaRect(s1)
        for s2 in contours:
            if s1 is not s2:
            
                s2box = cv2.minAreaRect(s2)
                #print(s1box)
                #print(s2box)
                
                angleSigma = 10
                
                if(s1box[2] < s2box[2] + 10 and s1box[2] > s2box[2] - 10):
                    if s1box[1][1] == 0 or s2box[1][1] == 0: continue
                    centerDistance = distance(s1box[0][0], s1box[0][1], s2box[0][0], s2box[0][1])
                    ratioToTop = centerDistance/s1box[1][1]
                    ratioToBottom = centerDistance/s2box[1][1]
                    heightSigma = 0.25
                    if ratioToTop < 1.25 + heightSigma and ratioToTop > 1.25 - heightSigma:
                        betweenHeightSigma = 0.3
                        betweenHeightRatio = centerDistance - (0.5*(s2box[1][1]+s1box[1][1]))/s1box[1][1]
                        if (betweenHeightRatio < 50) and (betweenHeightRatio > 20):
                            area1 = s1box[1][0]*s1box[1][1]
                            area2 = s2box[1][0]*s2box[1][1]
                            areaRatio = area1/area2
                            areaSigma = 0.5
                            if areaRatio < 1.5 + areaSigma and areaRatio > 1.5 - areaSigma:
                                x_offset = int(s1box[0][0])
                                y_offset = int(s1box[0][1])
                                foundFrames += 1
                                s1rot = np.int0(cv2.boxPoints(s1box))
                                s2rot = np.int0(cv2.boxPoints(s2box))
                                cv2.drawContours(displayed, [s1rot], 0, (0, 0, 255), 2)
                                cv2.drawContours(displayed, [s2rot], 0, (0, 0, 255), 2)
                                cv2.line(displayed, (int(s1box[0][0]), int(s1box[0][1])), (int(s2box[0][0]), int(s2box[0][1])), (255, 0, 0), 2)
    
    '''
    larger = len(contours)-1 if len(contours) > shapes else shapes
    for i in range(shapes):
        #print(i)
        try:
            curCont = contours[i]
            shapeContours.append(i)
        except IndexError:
            continue
        
        M = cv2.moments(curCont)
        try:
            cx = int(M['m10']/M['m00'])
            cy = int(M['m01']/M['m00'])      #Calculates a center for a circle at the center of the object
            shape = sd.detect(curCont)    #Detect number of vertices, then display
            cv2.putText(displayed, shape, (cx - 15, cy - 10), cv2.FONT_HERSHEY_SIMPLEX, #Offsets text from center point
                .3, (255, 0, 0), 1) #fontsize, colour, line thickness
        except ZeroDivisionError:
            cx = 0
            cy = 0
        
        rect = cv2.minAreaRect(curCont)
        box = cv2.boxPoints(rect)
        box = np.int0(box)
        
        cv2.circle(displayed, (cx, cy), 3, (255, 0, 0), 1)
        cv2.drawContours(displayed, [box], 0, (0, 0, 255), 2)'''

    cv2.drawContours(displayed, contours, -1, (0, 255, 0), 1)
    #print(contours[0])

    # Display framerate
    millisPrev = millis
    millis = int(round(time.time() * 1000))
    pauseFR = -1 * pauseFR
    if pauseFR == False: 
        cv2.putText(displayed, str(millis - millisPrev), (15, 40), cv2.FONT_HERSHEY_SIMPLEX, #Compute delay then convert to string, put in upper left corner
            1, (255, 0, 0), 1)
    
    # Display the resulting frame
    cv2.imshow('image', displayed)
    if cv2.waitKey(1) & 0xFF == ord(' '):
        cv2.imwrite(sys.argv[1] + str(imageNum) +  '.png', saved)
        imageNum = imageNum + 1
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
