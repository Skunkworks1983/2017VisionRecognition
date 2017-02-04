# tracker.py
# Main file that (currently) is processing camera frames and trying to find the boiler, then send that x val over UDP to the roborio

import numpy as np 
import cv2, time, sys, math, classifiers, argparse, cCamera, socket

#Define send and receive ports for UDP communication
HOST = '10.19.83.41' 
HOST_RECV = ''
PORT = 5802

try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((HOST, PORT))
    print('Socket created!')
except socket.error:
    print("Socket creation failed (on robot network?)")
    time.sleep(1)


#Setup argument processing
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--inputType", type=str, default="file",
    help="what input type should be used")
ap.add_argument("-t", "--target", type=str, default="goal",
    help="what to detect")
args = vars(ap.parse_args())

#Create version constants based on the reported version
if cv2.__version__ == "3.2.0": version = 3
elif cv2.__version__ == "2.4.9.1": version = 2
else: print("Unkown openCV version!")

#Print out all of a np array
np.set_printoptions(threshold=np.nan)

#Define test file and cam object based on argument
fileName = "./testVideos/test8.h264" #file of the video to load
cam = cCamera.cCamera(args["inputType"], fileName)

#necesasry for the return of createTrackbar (literally does nothing)
def doNothing(val): 
    pass

#self explanatory
def pointInContour(pt, cnt):
    return cv2.pointPolygonTest(cnt, pt, True) > 0

#adds the x,y coords to an array when the mouse is clicked on the window (used for debugging)
clickedPoints = [(0, 0)]
def saveClick(event,x,y,flags,param):
    global clickedPoints
    if event == cv2.EVENT_LBUTTONDOWN:
        clickedPoints.append((x,y))

#map [-width, width] -> [-1, 1] (so roborio doesn't have to care about window resolution)
def map(val, width):
    return ((2*val + 0.0)/width) - 1

DEBUG = False
HEADLESS = False #if we actually want GUI output

imageNum = 0

classifier = classifiers.cClassifier() #look in classifiers.py

# TODO need debug/performance mode
cv2.namedWindow('image')
cv2.setMouseCallback('image', saveClick)

#initialize these variables
width = 0
height = 0
lastKnown = ""
while(True):    
    # Capture frame-by-frame
    frame = cam.nextFrame() 
    
    #if the image is not tall and skinny, flip it
    #NOTE: Also flips over the y-axis
    if(frame.shape[1] > frame.shape[0]):
        frame = cv2.transpose(frame, frame)
    
    #resize the window and actually find the width and height
    frame = cv2.resize(frame, (0,0), fx=0.3, fy=0.3)
    width, height = frame.shape[1], frame.shape[0]
        
    saved = frame.copy() #to save the image if spacebar was pressed
    
    gray = frame[:,:,0]
    t_val = np.max(gray)*.90
    # Our operations on the frame come here
    #gray = cv2.cvtColor(gray, cv2.COLOR_BGR2GRAY) #Convert to gray, and then threshold based on t_val
    maxThresh = 255
    ret, thresholded = cv2.threshold(gray, t_val, maxThresh, cv2.THRESH_BINARY) #white if above thresh else black #comment uses wrong variable name
    
    #thresholded = np.uint8(np.clip(gray, np.percentile(gray, t_val), 100)) could try to switch to blue-scale later
    cv2.imshow("thresholded", thresholded)

    if (version == 2): contours, hierarchy = cv2.findContours(thresholded, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE) #Find the contours on the thresholded image
    else: contour_im, contours, hierarchy = cv2.findContours(thresholded, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE) #Find the contours on the thresholded image
    
    contours.sort(key = lambda s: -1 * len(s)) #Sort the list of contours by the length of each contour (smallest to biggest) - TODO killthis? is this the best proxy for interestingness?
    
    thresholded = cv2.cvtColor(thresholded, cv2.COLOR_GRAY2BGR) #turn it back to BGR so that when we draw things they show up in BGR
    
    found = False
    for s1 in contours:
        s1box = cv2.minAreaRect(s1)
        #long and skinny?
        '''if s1box[1][0] == 0 or float(s1box[1][1]) / s1box[1][0] < 1:
            print("Not long and skinny")
            continue'''
        for s2 in contours:
            if s1 is not s2:
                s2box = cv2.minAreaRect(s2)   #Compare all shapes against each other
                if s1box[1][1] == 0 or s2box[1][1] == 0: continue # 0 width contours are not interesting (and break when you divide by width)
                if not DEBUG:
                    if classifier.classify(s1box, s2box, False, args["target"]): #look at classifiers.py
                
                        if (version == 2):
                            s1rot = np.int0(cv2.cv.BoxPoints(s1box)) #draw the actual rectangles
                            s2rot = np.int0(cv2.cv.BoxPoints(s2box))
                        else:
                            s1rot = np.int0(cv2.boxPoints(s1box)) #draw the actual rectangles
                            s2rot = np.int0(cv2.boxPoints(s2box))
                        cv2.drawContours(frame, [s1rot], 0, (0, 0, 255), 2) #draw #Draw what?
                        cv2.drawContours(frame, [s2rot], 0, (0, 0, 255), 2)
                        cv2.line(frame, (int(s1box[0][0]), int(s1box[0][1])), (int(s2box[0][0]), int(s2box[0][1])), (255, 0, 0), 2) #draw a line connecting the boxes
                        xProportional = map(int(s1box[0][0]), width)
                        lastKnown = xProportional
                        sock.sendto(str(xProportional), (HOST, PORT))
                        found = True
    if not found: 
        sock.sendto(str(lastKnown), (HOST, PORT))
        #print(lastKnown)
    parsedContours = contours
    for i in clickedPoints:
        for k,v in enumerate(parsedContours[:]):
            if(pointInContour(i, v)):
                cv2.drawContours(frame, [v], -1, (255, 0, 0), 1)
                del parsedContours[k]
                
    cv2.drawContours(frame, parsedContours, -1, (0, 255, 0), 1)
    # Display the resulting frame
    
    cv2.imshow('image', frame)
    if cv2.waitKey(1) & 0xFF == ord(' '):
        cv2.imwrite(sys.argv[1] + str(imageNum) +  '.png', saved) #save the current image
        imageNum = imageNum + 1
    elif cv2.waitKey(1) & 0xFF == ord('c'):
        print("Cleared!")
        clickedPoints = [(0, 0)]
    elif cv2.waitKey(1) & 0xFF == ord('q'):
        break #die on q
