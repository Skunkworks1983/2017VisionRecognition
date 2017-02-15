# TODO header comments

import cv2, argparse, threading, Queue
try: import picamera, picamera.array
except: pass

lock = threading.Lock()
queue = Queue.Queue()
cleaningUp = False
doneCleaning = False

class cWriteVideo (threading.Thread):
    def __init__(self, videoName):
        threading.Thread.__init__(self)
        framerate = 20.0 # Technically does not matter, as we have no framerate control anyways, but we need to pass it something
        self.out = cv2.VideoWriter(videoName + '.avi', cv2.VideoWriter_fourcc(*'XVID'), framerate, (640, 480))
    def run(self):
        global cleaningUp
        while not cleaningUp:
            while not queue.empty():
                frame = queue.get(True, 0)
                queue.task_done()
                self.out.write(frame)
        self.out.release()
        global doneCleaning
        doneCleaning = True

class cCamera:
    def __init__(self, inputType, filename, videoName):

        self.inputType = inputType
        self.filename = filename
        self.videoName = videoName
        self.threads = []
        
        if(self.inputType.upper() == "PI" or self.inputType.upper() == "RASPI" or self.inputType.upper() == "PICAM"):
            self.camera = picamera.PiCamera()  # TODO look at cacheing this as with cap
            self.stream = picamera.array.PiRGBArray(self.camera)
            self.camera.resolution = (1280, 960)
            '''if self.videoName is not 'no': #Define the codec and create VideoWriter object for recording pi video
                framerate = 20.0 # Technically does not matter, as we have no framerate control anyways, but we need to pass it something
                global out
                out = cv2.VideoWriter(self.videoName + '.h264', cv2.cv.CV_FOURCC('H', '2', '6', '4'), framerate, self.camera.resolution)'''
                    
        elif(self.inputType.upper() == "VIDEO" or self.inputType.upper() == "FILE"):
            self.cap = cv2.VideoCapture(self.filename)
            
        elif(self.inputType.upper() == "WEBCAM" or self.inputType.upper() == "LAPTOP"):
            self.cap = cv2.VideoCapture(0)
        
        if self.videoName is not 'no':
            thread = cWriteVideo(self.videoName)
            thread.start()

    def getSysInfo(self):
        if cv2.__version__ == "3.2.0": version = 3
        elif cv2.__version__ == "2.4.9.1": version = 2
        else: print("Unkown openCV version!")
        
        return version

    def releaseCamera(self):
        global cleaningUp
        global doneCleaning
        cleaningUp = True
        try: self.cap.release()
        except: pass
        while not doneCleaning:
            time.sleep(100)
        
    def nextFrame(self):
        if(self.inputType.upper() == "PI" or self.inputType.upper() == "RASPI"):
            self.camera.capture(self.stream, 'bgr', use_video_port=True)
            frame = self.stream.array
            self.stream.seek(0)
            self.stream.truncate()
            frame = frame[20:960, 0:1200]
                
        elif(self.inputType.upper() == "VIDEO" or self.inputType.upper() == "FILE"):
            if not self.cap.grab(): #if the video has run out of frames
               self.cap = cv2.VideoCapture(self.filename) #reload the video and start again
               self.cap.grab()
            ret, frame = self.cap.retrieve()
            
        elif(self.inputType.upper() == "WEBCAM" or self.inputType.upper() == "LAPTOP"):
            ret, frame = self.cap.retrieve()
        
        if self.videoName is not 'no':
            queue.put(frame.copy())
            print(queue.qsize())
        
        return frame