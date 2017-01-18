import numpy as np
import cv2

cap = cv2.VideoCapture(0)

def doNothing(val):
    pass

t_val = 10
shapes = 2
cv2.namedWindow("trackbar")
cv2.createTrackbar("t_val", "trackbar", t_val, 255, doNothing) #Creates a trackbar on the window "trackbar" to adjust t_val (threshold)
cv2.createTrackbar("shapes", "trackbar", shapes, 100, doNothing) #Creates a trackbar on the window "trackbar" to adjust shapes (total recs found)

while(True):
    # Capture frame-by-frame
    ret, frame = cap.read()
    t_val = cv2.getTrackbarPos("t_val", "trackbar")       #Update the image and trackbar positions
    shapes = cv2.getTrackbarPos("shapes", "trackbar")

    # Our operations on the frame come here
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)                       #Convert to gray, and then threshold based on t_val
    ret, thresholded = cv2.threshold(gray, t_val, 255,cv2.THRESH_BINARY)

    contour_img, contours, hierarchy = cv2.findContours(thresholded, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE) #Find the contours on the thresholded image
    
    contours.sort(key = lambda s: len(s)) #Sort the list of contours by the length of each contour (smallest to biggest)
    
    thresholded = cv2.cvtColor(thresholded, cv2.COLOR_GRAY2BGR)
    
    larger = len(contours)-1 if len(contours) > shapes else shapes
    #print(larger)
    #print(contours)
    shapeContours = []
    for i in range(shapes):
        #print(i)
        try:
            curCont = contours[-1*(i+1)]
            shapeContours.append(-1*(i+1))
        except IndexError:
            continue
        
        M = cv2.moments(curCont)
        try:
            cx = int(M['m10']/M['m00'])
            cy = int(M['m01']/M['m00'])      #Calculates a center for a circle at the center of the object
        except ZeroDivisionError:
            cx = 0
            cy = 0
        
        rect = cv2.minAreaRect(curCont)
        box = cv2.boxPoints(rect)
        box = np.int0(box)
        
        cv2.circle(thresholded, (cx, cy), 3, (255, 0, 0), 1)
        cv2.drawContours(thresholded, [box], 0, (0, 0, 255), 2)

    cv2.drawContours(thresholded, contours, -1, (0, 255, 0), 1)
    #print(contours[0])

    # Display the resulting frame
    cv2.imshow('frame', thresholded)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
