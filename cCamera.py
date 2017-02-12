# TODO header comments

import cv2, argparse
try: import picamera, picamera.array
except: pass

class cCamera:
    def __init__(self, inputType, filename, videoName):

        self.inputType = inputType
        self.filename = filename
        self.videoName = videoName
        
        if(self.inputType.upper() == "PI" or self.inputType.upper() == "RASPI" or self.inputType.upper() == "PICAM"):
            self.camera = picamera.PiCamera()  # TODO look at cacheing this as with cap
            self.stream = picamera.array.PiRGBArray(self.camera)
            self.camera.resolution = (1280, 960)
                    
        elif(self.inputType.upper() == "VIDEO" or self.inputType.upper() == "FILE"):
            self.cap = cv2.VideoCapture(self.filename)
            
        elif(self.inputType.upper() == "WEBCAM" or self.inputType.upper() == "LAPTOP"):
            self.cap = cv2.VideoCapture(0)

        # Define the codec and create VideoWriter object
        framerate = 20.0 # Technically does not matter, as we have no framerate control anyways, but we need to pass it something.
        out = cv2.VideoWriter(self.videoName + '.h264',CV_FOURCC('H','2','6','4'), framerate, self.camera.resolution)

    def getSysInfo(self):
        if cv2.__version__ == "3.2.0": version = 3
        elif cv2.__version__ == "2.4.9.1": version = 2
        else: print("Unkown openCV version!")
        
        return version

    def writeVideo(self, frame):
        out.write(frame)
        
    def nextFrame(self):
        if(self.inputType.upper() == "PI" or self.inputType.upper() == "RASPI"):
            self.camera.capture(self.stream, 'bgr', use_video_port=True)
            frame = self.stream.array
            self.stream.seek(0)
            self.stream.truncate()
            frame = frame[20:960, 0:1200]
            return frame
                
        elif(self.inputType.upper() == "VIDEO" or self.inputType.upper() == "FILE"):
            if not self.cap.grab(): #if the video has run out of frames
               #print("Not cap grab")
               #print("Percentage found: " + str(foundFrames/frameCount))
               self.cap = cv2.VideoCapture(self.filename) #reload the video and start again
               self.cap.grab()
            ret, frame = self.cap.retrieve()
            return frame
            
        elif(self.inputType.upper() == "WEBCAM" or self.inputType.upper() == "LAPTOP"):
            ret, frame = self.cap.retrieve()
            return frame
