from cShapeDetector import cShapeDetector
import numpy as np
import cv2, time, sys, math, classifiers

np.set_printoptions(threshold=np.nan)

def loadCapture(filename): 
    return cv2.VideoCapture(filename) 
    
fileName = "./testPhotos/test1.h264" #file of the video to load
cap = loadCapture(fileName) #set to 0 if you want to capture from the webcam

def doNothing(val): #necesasry for the return of createTrackbar
    pass

t_val = 60 #starting threshold on the slider
imageNum = 0
cv2.namedWindow("trackbar", cv2.WINDOW_NORMAL)
cv2.createTrackbar("t_val", "trackbar", t_val, 255, doNothing) #Creates a trackbar on the window "trackbar" to adjust t_val (threshold)

frameCount = 0.1 #float so that we get float division
foundFrames = 0
    
classifier = classifiers.cClassifier() #look in classifiers.py

while(True):
    frameCount += 1
    # Capture frame-by-frame
    if not cap.grab(): #if the video has run out of frames
        print("Not cap grab")
        print("Percentage found: " + str(foundFrames/frameCount))
        cap = loadCapture(fileName) #reload the video and start again
        cap.grab() 
    ret, frame = cap.retrieve() #get a frame
    
    saved = frame.copy() #to save the image if spacebar was pressed
    
    t_val = cv2.getTrackbarPos("t_val", "trackbar")       #Update the image and trackbar positions

    # Our operations on the frame come here
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) #Convert to gray, and then threshold based on t_val
    maxThresh = 255
    ret, thresholded = cv2.threshold(gray, t_val, maxThresh ,cv2.THRESH_BINARY) #white if above thresh else black
    
    #thresholded = np.uint8(np.clip(gray, np.percentile(gray, t_val), 100)) could try to switch to blue-scale later
    cv2.imshow("thresholded", thresholded)

    contour_img, contours, hierarchy = cv2.findContours(thresholded, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE) #Find the contours on the thresholded image
    
    contours.sort(key = lambda s: -1 * len(s)) #Sort the list of contours by the length of each contour (smallest to biggest)
    
    thresholded = cv2.cvtColor(thresholded, cv2.COLOR_GRAY2BGR) #turn it back to BGR so that when we draw things they show up in BGR
    
    displayed = frame #make a copy of the frame  
    
    for s1 in contours:
        s1box = cv2.minAreaRect(s1)
        for s2 in contours:
            if s1 is not s2:
                s2box = cv2.minAreaRect(s2)   #Compare all shapes against each other
                if s1box[1][1] == 0 or s2box[1][1] == 0: continue
                
                if classifier.classify(s1box, s2box): #look at classifiers.py
                    foundFrames += 1
                    s1rot = np.int0(cv2.boxPoints(s1box)) #draw the actual rectangles
                    s2rot = np.int0(cv2.boxPoints(s2box))
                    cv2.drawContours(displayed, [s1rot], 0, (0, 0, 255), 2) #draw 
                    cv2.drawContours(displayed, [s2rot], 0, (0, 0, 255), 2)
                    cv2.line(displayed, (int(s1box[0][0]), int(s1box[0][1])), (int(s2box[0][0]), int(s2box[0][1])), (255, 0, 0), 2) #draw a line connecting the boxes

    cv2.drawContours(displayed, contours, -1, (0, 255, 0), 1)
    
    # Display the resulting frame
    cv2.imshow('image', displayed)
    if cv2.waitKey(1) & 0xFF == ord(' '):
        cv2.imwrite(sys.argv[1] + str(imageNum) +  '.png', saved) #save the current image
        imageNum = imageNum + 1
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break #die on q
