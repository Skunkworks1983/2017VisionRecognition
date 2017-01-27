import cv2, picamera, picamera.array

class cCamera:
    def __init__(self, inputType, filename):

        self.inputType = inputType
        
        if(self.inputType.upper() == "PI" or self.inputType.upper() == "RASPI" or self.inputType.upper() == "PICAM"):
            with picamera.PiCamera() as self.camera:
                with picamera.array.PiRGBArray(self.camera) as self.stream:
                    self.camera.resolution = (320, 240)
                    
        elif(self.inputType.upper() == "VIDEO" or self.inputType.upper() == "FILE"):
            self.cap = cv2.VideoCapture(filename)
            
        elif(self.inputType.upper() == "WEBCAM" or self.inputType.upper() == "LAPTOP"):
            self.cap = cv2.VideoCapture(0)

    def nextFrame(self):
        if(self.inputType.upper() == "PI" or self.inputType.upper() == "RASPI"):
            with picamera.PiCamera() as self.camera:
                with picamera.array.PiRGBArray(self.camera) as self.stream:
                    self.camera.capture(self.stream, 'bgr', use_video_port=True)
                    frame = self.stream.array
                    self.stream.seek(0)
                    self.stream.truncate()
                    return frame
                
        elif(self.inputType.upper() == "VIDEO" or self.inputType.upper() == "FILE"):
            if not self.cap.grab(): #if the video has run out of frames
               #print("Not cap grab")
               #print("Percentage found: " + str(foundFrames/frameCount))
               self.cap = loadCapture(self.fileName) #reload the video and start again
               self.cap.grab()
            ret, frame = self.cap.retrieve()
            return frame
        elif(self.inputType.upper() == "WEBCAM" or self.inputType.upper() == "LAPTOP"):
            ret, frame = self.cap.retrieve()
            return frame
