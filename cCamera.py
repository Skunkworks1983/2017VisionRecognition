# cCamera.py
# A class that is used to simplify and standardize the various methods of video streaming.
# It also contains code to create a seperate thread that writes the recorded video to file.

import cv2, argparse, threading, time, Queue
try: import picamera, picamera.array
except: pass

lock = threading.Lock()
queue = Queue.Queue()
cleaningUp = False
doneCleaning = False
piResolution = (1280, 960)

# cWriteVideo is a thread designed to save video. It pulls its frames from the queue object, which manages locking for me.
class cWriteVideo (threading.Thread):
    def __init__(self, videoName, version):
        threading.Thread.__init__(self)
        global piResolution
        framerate = 20.0 # Technically does not matter, as we have no framerate control anyways, but we need to pass it something
        if version == 3: self.out = cv2.VideoWriter(videoName + '.avi', cv2.VideoWriter_fourcc(*'XVID'), framerate, (640, 480))
        else: out = cv2.VideoWriter(self.videoName + '.avi', cv2.cv.CV_FOURCC(*'XVID'), framerate, piResolution)
    def run(self):
        global cleaningUp
        while not cleaningUp:
            while not queue.empty():
                #print(queue.qsize()) # It can be useful for debug purposes to know how large the working queue is.
                frame = queue.get(False)
                queue.task_done()
                self.out.write(frame)
        self.out.release() # Finalize video saving. If your video is corrupted, it is because this did not get called successfully.
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
            self.camera.resolution = piResolution
                    
        elif(self.inputType.upper() == "VIDEO" or self.inputType.upper() == "FILE"):
            self.cap = cv2.VideoCapture(self.filename)
            
        elif(self.inputType.upper() == "WEBCAM" or self.inputType.upper() == "LAPTOP"):
            self.cap = cv2.VideoCapture(0)
        
        if self.videoName is not 'no':
            thread = cWriteVideo(self.videoName, self.getSysInfo())
            thread.start()

    def getSysInfo(self):
        if cv2.__version__ == "3.2.0": version = 3
        elif cv2.__version__ == "2.4.9.1": version = 2
        else: print("Unkown openCV version!")

        return version

    def releaseCamera(self):
        global cleaningUp, doneCleaning
        cleaningUp = True
        try: self.cap.release()
        except: pass
        if doneCleaning is False:
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
        
        return frame