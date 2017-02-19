#!/usr/bin/python

# tracker.py
# Main file that is processing camera frames and trying to find the vision target, then send that val over UDP to the roborio

from __future__ import division #IMPORTANT: Float division will work as intended (3/2 == 1.5 instead of 1, no need to do 3.0/2 == 1.5)
import numpy as np 
import cv2, time, sys, math, classifiers, argparse, cCamera, riosocket, os, socket

# where are we running? Get hostname then drop the "-pi" from gear-pi or goal-pi
targetFromHostname = socket.gethostname()[:-3] 
if targetFromHostname != 'gear' and targetFromHostname != 'goal' :
    targetFromHostname = 'goal' # no GPIO header installed, choose a sane default

#####      ARG PARSING      #####
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--inputType", type=str, default="pi",
    help="what input type should be used")
ap.add_argument("-t", "--target", type=str, default=targetFromHostname,
    help="what to detect")
ap.add_argument("-m", "--minT_val", type=int, default=230,
    help="how hard to threshold")
ap.add_argument("-v", "--videoName", type=str, default="no",
    help="name of video (input nothing to not save video)")
ap.add_argument("-d", "--DEBUG", type=bool, default=False,
    help="whether to output debug vals")
ap.add_argument("-e", "--HEADLESS", type=bool, default=False,
    help="whether to display images")
args = vars(ap.parse_args())
inputType = args['inputType'] 
target = args['target']
minT_val = args['minT_val']
videoName = args['videoName']
DEBUG = args['DEBUG']
HEADLESS = args['HEADLESS']
#################################

#####  VARIOUS DECLERATION  #####
classifier = classifiers.cClassifier()

if not HEADLESS: cv2.namedWindow('image')

#various variables that are counters or placeholders for later
lastKnown = ""
imageNum = 0

#list of ms it took to iterate through (for fps management)
times = []

#Print out all of a np array (only matters if we're in debug mode)
if DEBUG: np.set_printoptions(threshold=np.nan)
#################################

#####       FUNCTIONS       #####
#self explanatory
def pointInContour(pt, cnt):
    return cv2.pointPolygonTest(cnt, pt, True) > 0

#map [-width, width] -> [-1, 1] (so robot code doesn't have to care about window resolution)
def map(val, width):
    return ((2*val/width) - 1)

def checkKeypresses():
    '''global times

    t1 = current_milli_time()
    
    tD = t1 - t0
    times.append(tD)
    times = times[-20:]
    avgMsPerFrame = sum(times)/len(times)
    sPerFrame = avgMsPerFrame / 1000
    fps = 1 / sPerFrame
    print("FPS: " + str(fps))'''
    
    if not HEADLESS: cv2.imshow('image', frame)
    
    if DEBUG and cv2.waitKey(1) & 0xFF == ord(' '):
        cv2.imwrite(sys.argv[1] + str(imageNum) +  '.png', saved) #save the current image
        imageNum = imageNum + 1
    elif cv2.waitKey(1) & 0xFF == ord('q'):
        cam.releaseCamera()
        sys.exit() #die on q
    
#quick and dirty function to get milliseconds from the time module
current_milli_time = lambda: int(round(time.time() * 1000))
#################################

##### SOCKET INITIALIZATION #####
riosocket = riosocket.RioSocket()
#################################

##### CAMERA INITIALIZATION #####
#Define test file and cam object based on argument
fileName = "./test16.h264" #file of the video to load
cam = cCamera.cCamera(inputType, fileName, videoName)
version = cam.getSysInfo() # Not technically part of camera, but cCamera will always be where opencv is, so it's good to have the version function there
#################################

## MAIN CODE (HERE BE DRAGONS) ##    
while(True):
    #Get time start (for fps management)
    t0 = current_milli_time()

    # Capture frame-by-frame
    frame = cam.nextFrame()
    
    #if the image is not tall, skinny, and is a goal cam flip it
    #NOTE: Also flips over the y-axis
    if(frame.shape[1] > frame.shape[0] and target is 'goal'):
        frame = cv2.transpose(frame, frame)
    
    #resize the window and actually find the width and height
    '''frame = cv2.resize(frame, (0,0), fx=0.3, fy=0.3)'''
    width, height = frame.shape[1], frame.shape[0]
       
    #Copying mats seems heavy on the drive if we're going to be trying to save video
    if DEBUG: saved = frame.copy() #to save the image if spacebar was pressed 
    
    # Our operations on the frame come here
    #gray = cv2.cvtColor(gray, cv2.COLOR_BGR2GRAY) #Convert to gray, and then threshold based on t_val
    gray = frame[:,:,0] # pull just one channel
    t_val = np.max(gray)*.90 # drop the lowest brightness pixels
    if t_val < minT_val: t_val = minT_val # but in a very dim scene its ok to drop everything
    else: pass
    
    maxThresh = 255
    ret, thresholded = cv2.threshold(gray, t_val, maxThresh, cv2.THRESH_BINARY) #white if above thresh else black
    
    #thresholded = cv2.blur(thresholded,(5,5))
    
    #thresholded = np.uint8(np.clip(gray, np.percentile(gray, t_val), 100)) could try to switch to blue-scale later
    if not HEADLESS: cv2.imshow("thresholded", thresholded)

    if (version == 2): 
        contours, hierarchy = cv2.findContours(thresholded, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE) #Find the contours on the thresholded image
    else: 
        contour_im, contours, hierarchy = cv2.findContours(thresholded, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE) #Find the contours on the thresholded image
    
    contours.sort(key = lambda s: -1 * len(s)) #Sort the list of contours by the length of each contour (smallest to biggest) - Actually useful now, used to make sure only one gear retrieval is found
    
    if not HEADLESS:
        thresholded = cv2.cvtColor(thresholded, cv2.COLOR_GRAY2BGR) #turn it back to BGR so that when we draw things they show up in BGR        
    
    found = False
    
    if len(contours) > 10: 
        if DEBUG: print 'To many contours to process'
        checkKeypresses()
        continue
    
    for s1 in contours:
        if found:
            break
        s1box = cv2.minAreaRect(s1)
        if s1box[1][1] == 0: continue
        for s2 in contours:
            if s1 is not s2:
                s2box = cv2.minAreaRect(s2)   #Compare all shapes against each other
                if s2box[1][1] == 0: continue # 0 width contours are not interesting (and skip if you have to divide by width)
                if not DEBUG:
                    if classifier.classify(s1box, s2box, DEBUG, target): #look at classifiers.py
                        if not HEADLESS:
                            if (version == 2):
                                s1rot = np.int0(cv2.cv.BoxPoints(s1box)) #draw the actual rectangles
                                s2rot = np.int0(cv2.cv.BoxPoints(s2box))
                            else:
                                s1rot = np.int0(cv2.boxPoints(s1box)) #draw the actual rectangles
                                s2rot = np.int0(cv2.boxPoints(s2box))
                                
                            cv2.drawContours(frame, [s1rot], 0, (0, 0, 255), 2) #draw #Draw what?
                            cv2.drawContours(frame, [s2rot], 0, (0, 0, 255), 2)
                            cv2.line(frame, (int(s1box[0][0]), int(s1box[0][1])), (int(s2box[0][0]), int(s2box[0][1])), (255, 0, 0), 2) #draw a line connecting the boxes
                        if DEBUG: 
                            print 'Size ratio: ' + str((s1box[1][0]*s1box[1][1])/(s2box[1][0]*s2box[1][1]))
                            if DEBUG > 1 and (s1box[1][0]*s1box[1][1])/(s2box[1][0]*s2box[1][1]): print 'To the left'
                            else: print 'To the right '
                        xProportional = map(int(s1box[0][0]), width)
                        lastKnown = xProportional
                        if target == "goal":
                            riosocket.send("goal", True, str(xProportional))
                        else:
                            riosocket.send("gear", True, str(xProportional))
                        if DEBUG : print("Found: " + str(xProportional))
                        found = True
                        break

    if not found: 
        if target == "goal":
            riosocket.send("goal", False, str(lastKnown))
        else:
            riosocket.send("gear", False, str(lastKnown))
        '''print("Last:  " + str(lastKnown))'''

    # RIOSOCKET SHUTDOWN PROTOCOL
    data, address = riosocket.recv(MSG_LEN)

    if(data == "shutdown"):
        cam.releaseCamera()
        os.system("sudo shutdown -h now")
        
    checkKeypresses()
    
