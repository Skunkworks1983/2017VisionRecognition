'''
Approximates the number of verticies in a given contour using this algorith: https://en.wikipedia.org/wiki/Ramer%E2%80%93Douglas%E2%80%93Peucker_algorithm
                                                                           ^insert an m
'''

# import the necessary packages
import cv2
#move descriptive header here so that its obvious its associated with this and not the file
class cShapeDetector:
    def __init__(self):
        #you should do definition like on line 15 in __init__
        pass

    def detect(self, c):
        # initialize the m_shape name and approximate the contour
        m_shape = "unidentified" #ya gotta do self.
        m_peri = cv2.arcLength(c, True)
        m_approx = cv2.approxPolyDP(c, 0.04 * m_peri, True) #magic number

        # if the m_shape is a triangle, it will have 3 vertices
        if len(m_approx) == 3:
            m_shape = "triangle"

        # if the m_shape has 4 vertices, it is either a square or
        # a rectangle
        elif len(m_approx) == 4:
            # compute the bounding box of the contour and use the
            # bounding box to compute the aspect ratio
            (x, y, w, h) = cv2.boundingRect(m_approx)
            m_ar = w / float(h) #m_ar ?

            # a square will have an aspect ratio that is approximately
            # equal to one, otherwise, the m_shape is a rectangle
            m_shape = "square" if m_ar >= 0.95 and m_ar <= 1.05 else "rectangle" #put parenthesis around your conditional
                                                                                 #(m_ar >= 0.95 and m_ar < 1.05)
                                                                                 #be careful about ternarys

        # if the m_shape is a pentagon, it will have 5 vertices
        elif len(m_approx) == 5:
            m_shape = "pentagon"

        # otherwise, we assume the m_shape is a circle
        else:
            m_shape = "circle"

        # return the name of the m_shape
        #^^^unnecessary
        return m_shape