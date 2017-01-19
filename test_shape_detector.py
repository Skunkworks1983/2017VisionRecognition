'''
This is a basic test file to find the number of verticies in a contour with an area over a certain size, and then display it.
It uses shape_detector.py to determine the number of verticies, and then display it.
'''

# import the necessary packages
from cShapeDetector import cShapeDetector
import numpy as np
import sys
import imutils
import cv2

originalIm = cv2.imread(sys.argv[1])

cv2.imshow("Original Image", originalIm)
cv2.waitKey(0)
cv2.destroyAllWindows()

thresh = int(sys.argv[2])
print(thresh)

sd = cShapeDetector()

# convert image to grayscale, blur it slightly,
# and threshold it
grayIm = cv2.cvtColor(originalIm, cv2.COLOR_BGR2GRAY)

cv2.imshow("Gray Image", grayIm)
cv2.waitKey(0)
cv2.destroyAllWindows()

blurredIm = cv2.GaussianBlur(grayIm, (5, 5), 0)

cv2.imshow("Gaussian Image", blurredIm)
cv2.waitKey(0)
cv2.destroyAllWindows()

binaryIm = cv2.threshold(blurredIm, thresh, 255, cv2.THRESH_BINARY) [1]

cv2.imshow("Binary Image", binaryIm)
cv2.waitKey(0)
cv2.destroyAllWindows()

#standardize display image
displayIm = originalIm
if displayIm.all() != originalIm.all():
    displayIm = cv2.cvtColor(displayIm, cv2.COLOR_GRAY2BGR)

# find contours in the thresholded image and initialize the
# shape detector
cnts = cv2.findContours(binaryIm, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
cnts = cnts[0] if imutils.is_cv2() else cnts[1]



# loop over the contours
for c in cnts:
    print("found contour")
 
    # compute the center of the contour, then detect the name of the
    # shape using only the contour
    M = cv2.moments(c)
    if M["m00"] > 10000:
        try:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            shape = sd.detect(c)

            # multiply the contour (x, y)-coordinates by the resize ratio,
            # then draw the contours and the name of the shape on the image
            cv2.drawContours(displayIm, [c], -1, (0, 0, 255), 2)
            cv2.putText(displayIm, shape, (cX, cY), cv2.FONT_HERSHEY_SIMPLEX,
                1, (0, 0, 255), 2)
            print("found shapes")
        except ZeroDivisionError:
            print("oops")
    else:
        print("contour to small")

# show the output image 
displayIm = cv2.resize(displayIm, (1280, 800))
cv2.imshow("Image", displayIm)
        
cv2.waitKey(0)
    
cv2.destroyAllWindows()