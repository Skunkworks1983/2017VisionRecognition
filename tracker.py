from cShapeDetector import cShapeDetector
import numpy as np
import cv2, time, sys, math, classifiers, argparse, cCamera

ap = argparse.ArgumentParser()
ap.add_argument("-i", "--inputType", type=str, default=file,
	help="what input type should be used")
args = vars(ap.parse_args())
    
fileName = "./testPhotos/test1.h264" #file of the video to load
cam = cCamera.cCamera(args["inputType"], fileName)

if cv2.__version__ == "3.2.0": version = 3
elif cv2.__version__ == "2.4.9.1": version = 2
else: print("Unkown openCV version!")

np.set_printoptions(threshold=np.nan)


def doNothing(val): #necesasry for the return of createTrackbar
    pass

t_val = 60 #starting threshold on the slider
imageNum = 0
cv2.namedWindow("trackbar", cv2.WINDOW_NORMAL)
cv2.createTrackbar("t_val", "trackbar", t_val, 255, doNothing) #Creates a trackbar on the window "trackbar" to adjust t_val (threshold)

frameCount = 0.1 #float so that we get float division
foundFrames = 0
    
classifier = classifiers.cClassifier() #look in classifiers.py

while True:
    frame = cam.nextFrame()
    saved = frame.copy()
    
    frameCount += 1
            
    t_val = cv2.getTrackbarPos("t_val", "trackbar")       #Update the image and trackbar positions

    # Our operations on the frame come here
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) #Convert to gray, and then threshold based on t_val
    maxThresh = 255
    ret, thresholded = cv2.threshold(gray, t_val, maxThresh ,cv2.THRESH_BINARY) #white if above thresh else black
    
    #thresholded = np.uint8(np.clip(gray, np.percentile(gray, t_val), 100)) could try to switch to blue-scale later
    cv2.imshow("thresholded", thresholded)

    if (version == 2): contours, hierarchy = cv2.findContours(thresholded, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE) #Find the contours on the thresholded image
    else: contour_im, contours, hierarchy = cv2.findContours(thresholded, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE) #Find the contours on the thresholded image
    
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
                    if (version == 2):
                        s1rot = np.int0(cv2.cv.BoxPoints(s1box)) #draw the actual rectangles
                        s2rot = np.int0(cv2.cv.BoxPoints(s2box))
                    else:
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
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break #die on q
