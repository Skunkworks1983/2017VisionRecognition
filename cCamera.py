# cCamera.py
# A class that is used to simplify and standardize the various methods of video streaming.
# It also contains code to create a seperate thread that writes the recorded video to file.

import cv2, argparse, threading, time, Queue, logging, sys
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
        print('Exiting cWriteVideo thread...')

class cCamera:
    def __init__(self, inputType, filename):

        self.inputType = inputType
        self.filename = filename
        self.save = False
        self.saveStarted = False
        
        if(self.inputType.upper() == "PI" or self.inputType.upper() == "RASPI" or self.inputType.upper() == "PICAM"):
            logging.info('Creating pi camera...')
            try:
                self.camera = picamera.PiCamera()  # TODO look at cacheing this as with cap
                self.stream = picamera.array.PiRGBArray(self.camera)
                self.camera.resolution = piResolution
                time.sleep(1)
            except:
                logging.critical('Failed to create camera!')
                sys.exit()
                    
        elif(self.inputType.upper() == "VIDEO" or self.inputType.upper() == "FILE"):
            try: self.cap = cv2.VideoCapture(self.filename)
            except: logging.critical('File does not exist!')
            
        elif(self.inputType.upper() == "WEBCAM" or self.inputType.upper() == "LAPTOP"):
            try: self.cap = cv2.VideoCapture(0)
            except: logging.critical('Failed to create webcam!')

    def getSysInfo(self):
        if cv2.__version__ == "3.2.0": version = 3
        elif cv2.__version__ == "2.4.9.1": version = 2
        else: print("Unkown openCV version!")

        return version

    def startVideoSave(self, videoName):
        self.save = True
        if not self.saveStarted:
            self.saveStarted = True
            thread = cWriteVideo(videoName, self.getSysInfo())
            thread.start()
        
    def releaseCamera(self):
        try: self.cap.release()
        except: pass
    
    def releaseVideo(self):
        global cleaningUp, doneCleaning
        cleaningUp = True
        if doneCleaning is False:
            time.sleep(100)

    def nextFrame(self):
        if(self.inputType.upper() == "PI" or self.inputType.upper() == "RASPI"):
            self.camera.capture(self.stream, 'bgr', use_video_port=True)
            frame = self.stream.array
            self.stream.seek(0)
            self.stream.truncate()
            #frame = frame[20:960, 0:1200] # This was the software solution to the led ring getting into the frame. The new mount should fix this
                
        elif(self.inputType.upper() == "VIDEO" or self.inputType.upper() == "FILE"):
            if not self.cap.grab(): #if the video has run out of frames
               self.cap = cv2.VideoCapture(self.filename) #reload the video and start again
               self.cap.grab()
            ret, frame = self.cap.retrieve()
            
        elif(self.inputType.upper() == "WEBCAM" or self.inputType.upper() == "LAPTOP"):
            ret, frame = self.cap.retrieve()
	
        else: print('um waht')
        
        if self.save:
            queue.put(frame.copy())
        
        return frame
