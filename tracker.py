#!/usr/bin/python

# tracker.py
# Main file that is processing camera frames and trying to find the vision target,
# then send that val over UDP to the roborio.

from __future__ import \
    division  # IMPORTANT: Float division will work as intended (3/2 == 1.5 instead of 1, no need to do 3.0/2 == 1.5)
import numpy as np
import cv2
import time
import sys
import classifiers
import argparse
import cCamera
import riosocket
import os
import socket
import logging

# Comment

# Code sections, now with more PEP 8
# A E S T H E T I C S

# -----    CHECK HOSTNAME    -----
# We need to know if we're on the gear pi or the goal pi
targetFromHostname = socket.gethostname()[:-3]
if targetFromHostname != 'gear' and targetFromHostname != 'goal':
    targetFromHostname = 'goal'  # no GPIO header installed, choose a sane default
# ---------------------------------

# -----      ARG PARSING      -----
# If your running from a command line its useful to be able to put in some debug options.
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--inputType", type=str, default="pi", help="what input type should be used")
ap.add_argument("-t", "--target", type=str, default="goal", help="what to detect")
ap.add_argument("-m", "--minT_val", type=int, default=230, help="how hard to threshold")
ap.add_argument("-s", "--saveVideo", type=str, default='False', help="whether to save video or not")
ap.add_argument("-d", "--DEBUG", type=str, default='False', help="whether to output debug vals")
ap.add_argument("-e", "--HEADLESS", type=str, default='True',
                help="whether to display images")  # Passing anything is how you set it to true,
ap.add_argument("-v", "--videosend", type=str, default='False', help="whether to send vid over udp")
args = vars(ap.parse_args())
inputType = args['inputType']
target = args['target']
minT_val = args['minT_val']
if args['saveVideo'] is 'True':
    saveVideo = True  # Arg parse actually does everything in strings, so we have to process bools ourselves
else:
    saveVideo = False
if args['DEBUG'] == 'True':
    DEBUG = True
else:
    DEBUG = False
if args['HEADLESS'] == 'True':
    HEADLESS = True
else:
    HEADLESS = False
if args['videosend'] is 'True':
    videosend = True
else:
    videosend = False
print(args)
# ---------------------------------

# -----   CHANGE WORKING DIR  -----
# We want to put our logs and videos on any usb devices attached to the pis.
usbFound = False
if inputType == 'pi':
    time.sleep(20)  # Wait for the pi to turn on so we can find the usb drive
    for dirpath, dirs, files in os.walk("/media/pi"):
        print('step')
        if usbFound:
            continue
        for name in files:
            if name == 'paella':
                os.path.join(dirpath, name)
                os.chdir(dirpath)
                usbFound = True
                continue
        if usbFound:
            continue
        for name in dirs:
            if name == 'System Volume Information':
                os.path.join(dirpath, name)
                os.chdir(dirpath)
                usbFound = True
                continue
else:
    os.chdir('./Logs')  # Otherwise it's nice to not clutter up the repo, so stick logs in a differnt directory
# ---------------------------------

# -----      LOGGING INIT     -----
# If we're not on command line, it's very useful to have logs of what happened
logName = time.strftime("%m-%d-%H-%M-%S-", time.gmtime()) + socket.gethostname() + '.log'
logging.basicConfig(filename=logName, level=logging.DEBUG)
logging.info('Log initialized')
# ---------------------------------

# -----  VARIOUS DECLARATION  -----
# Things the while loop relies on
classifier = classifiers.cClassifier()

if not HEADLESS:
    cv2.namedWindow('image')

# Video writing
writing = False
oldData = 'Data not initialized'

# various variables that are counters or placeholders for later
lastKnown = "0"

# list of ms it took to iterate through (for fps management)
times = []

# Print out all of a np array (only matters if we're in debug mode)
if DEBUG:
    np.set_printoptions(threshold=np.nan)


# ---------------------------------

# -----       FUNCTIONS       -----
# Various functions to be used in other parts of the code
# map [-width, width] -> [-1, 1] (so robot code doesn't have to care about window resolution)
def map_res(val, width_map):
    return (2 * val / width_map) - 1


def cleanup():  # Run this at the end of the while loop, or when it is terminated early
    global HEADLESS
    if DEBUG:  # For displaying fps
        global times

        t1 = current_milli_time()

        t_d = t1 - t0
        times.append(t_d)
        times = times[-20:]
        avg_ms_per_frame = sum(times) / len(times)
        s_per_frame = avg_ms_per_frame / 1000
        fps = 1 / s_per_frame
        print("FPS: " + str(fps))

    if not HEADLESS:
        cv2.imshow('image', frame)

    if DEBUG and cv2.waitKey(1) & 0xFF == ord(' '):
        cv2.imwrite(("%m-%d-%H-%M-%S-", time.gmtime()) + socket.gethostname() + '.png', saved)  # save the current image

    elif cv2.waitKey(1) & 0xFF == ord('q'):
        logging.info('Recieved shutdown key.')
        riosocket.manualshutdown()

    if videosend:  # Send video over udp to the roborio
        riosocket.sendVid(frame)

    # RIOSOCKET SHUTDOWN & VIDEOSAVE PROTOCOL
    global writing
    global oldData

    data = riosocket.recv()
    if data == oldData:
        oldData = data
        data = 'repeated data'

    if data == "shutdown":
        logging.info('Received shutdown command.')
        logging.info('Releasing camera...')
        cam.releaseCamera()
        logging.info('Success!')
        if writing:
            cam.releaseVideo()
            logging.info('Released video')
        logging.info('Trust me.')
        os.system("sudo shutdown -h now")

    if data == 'shutdownq':  # If you recieve a q, you dont want to shutdown the computer.
        logging.info('Releasing camera...')
        cam.releaseCamera()
        logging.info('Success!')
        if writing:
            logging.info('Releasing video...')
            cam.releaseVideo()
            logging.info('Success!')
        logging.info('Exiting Program.')
        sys.exit()

    if data == "auto":  # For recording video
        logging.info('Starting auto video...')
        cam.startVideoSave(time.strftime("%m-%d-%H-%M-%S-", time.gmtime()) + 'auto' + target)
        writing = True
        logging.info('Success!')

    if data == "tele":
        if writing:
            logging.info('Releasing auto video...')
            cam.releaseVideo()
            logging.info('Success!')
        logging.info('Starting tele video...')
        cam.startVideoSave(time.strftime("%m-%d-%H-%M-%S-", time.gmtime()) + 'tele' + target)
        writing = True
        logging.info('Success!')

    if saveVideo:
        logging.info('Started saving dev video')
        cam.startVideoSave(time.strftime("%m-%d-%H-%M-%S-", time.gmtime()) + 'dev' + target)
        logging.info('Success!')


# quick and dirty function to get milliseconds from the time module
def current_milli_time():
    return lambda: int(round(time.time() * 1000))
# ---------------------------------

# ----- SOCKET INITIALIZATION -----
riosocket = riosocket.RioSocket(target)
logging.info('Created riosocket')
# ---------------------------------

# ----- CAMERA INITIALIZATION -----
# Define test file and cam object based on argument
fileName = "./test56.h264"  # file of the video to load
cam = cCamera.cCamera(inputType, fileName)
version = cam.getSysInfo()  # Not technically part of camera, but cCamera will always be where opencv is,
# so it's good to have the version function there
# --------------------------------

# ----- MAIN CODE (HERE BE DRAGONS) -----
while True:
    # Get time start (for fps management)
    t0 = current_milli_time()

    # Capture frame-by-frame
    if DEBUG:
        print('Getting frame')
    frame = cam.nextFrame()

    # if the image is not tall, skinny, and is a goal cam flip it
    # NOTE: Also flips over the y-axis
    if frame.shape[1] > frame.shape[0] and target is 'goal':
        frame = cv2.transpose(frame, frame)

    # resize the window and actually find the width and height
    '''frame = cv2.resize(frame, (0,0), fx=0.3, fy=0.3)'''
    width, height = frame.shape[1], frame.shape[0]

    # Copying mats seems heavy on the drive if we're going to be trying to save video
    if DEBUG:
        saved = frame.copy()  # to save the image if spacebar was pressed

    # Our operations on the frame come here
    # gray = cv2.cvtColor(gray, cv2.COLOR_BGR2GRAY) #Convert to gray, and then threshold based on t_val
    gray = frame[:, :, 0]  # pull just one channel
    t_val = np.max(gray) * .90  # drop the lowest brightness pixels
    if t_val < minT_val:
        t_val = minT_val  # but in a very dim scene its ok to drop everything
    else:
        pass

    maxThresh = 255
    ret, thresholded = cv2.threshold(gray, t_val, maxThresh, cv2.THRESH_BINARY)  # white if above thresh else black

    # thresholded = cv2.blur(thresholded,(5,5))

    # thresholded = np.uint8(np.clip(gray, np.percentile(gray, t_val), 100)) could try to switch to blue-scale later
    if not HEADLESS:
        cv2.imshow("thresholded", thresholded)

    if version == 2:  # OpenCV has differnt syntax in 3
        contours, hierarchy = cv2.findContours(thresholded, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        # Find the contours on the thresholded image
    else:
        contour_im, contours, hierarchy = cv2.findContours(thresholded, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        # Find the contours on the thresholded image

    contours.sort(key=lambda s: -1 * len(s))  # Sort the list of contours by the
    # length of each contour (smallest to biggest)

    if not HEADLESS:
        thresholded = cv2.cvtColor(thresholded, cv2.COLOR_GRAY2BGR)
        # turn it back to BGR so that when we draw things they show up in BGR

    found = False  # Because we just got the image so no targets have been found

    if len(contours) > 10:
        if DEBUG:
            print 'To many contours to process'
        cleanup()
        continue

    for s1 in contours:
        if found:
            break
        s1box = cv2.minAreaRect(s1)
        if s1box[1][1] == 0: continue  # Ignore contours with 0 width
        for s2 in contours:
            if s1 is not s2:  # Don't want to compare a contour to itself
                s2box = cv2.minAreaRect(s2)  # Compare all shapes against each other
                if s2box[1][1] == 0:
                    continue  # 0 width contours are not interesting (and skip if you have to divide by width)
                if classifier.classify(s1box, s2box, DEBUG, target):  # look at classifiers.py
                    if not HEADLESS:
                        if (version == 2):
                            s1rot = np.int0(cv2.cv.BoxPoints(s1box))  # draw the actual rectangles
                            s2rot = np.int0(cv2.cv.BoxPoints(s2box))
                        else:
                            s1rot = np.int0(cv2.boxPoints(s1box))  # draw the actual rectangles
                            s2rot = np.int0(cv2.boxPoints(s2box))

                        cv2.drawContours(frame, [s1rot], 0, (0, 0, 255), 2)  # draw contours
                        cv2.drawContours(frame, [s2rot], 0, (0, 0, 255), 2)
                        cv2.line(frame, (int(s1box[0][0]), int(s1box[0][1])), (int(s2box[0][0]), int(s2box[0][1])),
                                 (255, 0, 0), 2)  # draw a line connecting the boxes
                    if DEBUG:
                        print 'Size ratio: ' + str((s1box[1][0] * s1box[1][1]) / (s2box[1][0] * s2box[1][1]))
                        if DEBUG > 1 and (s1box[1][0] * s1box[1][1]) / (s2box[1][0] * s2box[1][1]):
                            print 'To the left'
                        else:
                            print 'To the right '
                    if target == 'goal':
                        xProportional = map_res(int(s1box[0][0]), width)
                    else:
                        xProportional = map_res(int((s1box[0][0] + s2box[0][0]) / 2), width)
                    lastKnown = xProportional
                    if target == "goal":
                        riosocket.send("goal", True, str(xProportional))
                    else:
                        riosocket.send("gear", True, str(xProportional))
                    if DEBUG:
                        print("Found: " + str(xProportional))
                    found = True
                    break

    if not found:
        if target == "goal":
            riosocket.send("goal", False, str(lastKnown))
        else:
            riosocket.send("gear", False, str(lastKnown))
        '''print("Last:  " + str(lastKnown))'''

    cleanup()
