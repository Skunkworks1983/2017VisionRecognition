import numpy as np
import socket, cCamera, argparse, cv2, time

ap = argparse.ArgumentParser()
ap.add_argument("-i", "--inputType", type=str, default="file",
    help="what input type should be used")
args = vars(ap.parse_args())

HOST = 'localhost'
PORT = 5555

fileName = "./testPhotos/test8.h264" #file of the video to load
cam = cCamera.cCamera(args["inputType"], fileName)
version = cam.getSysInfo()

try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print('Socket created!')
except:
    print('Socket creation fail!')

frame = cam.nextFrame()
print(frame.shape[1])
print(frame.shape[0])    
   
while(True):
    frame = cam.nextFrame()
    frame = cv2.resize(frame, (0,0), fx=0.1, fy=0.1)
    frame = frame[:,:,0]
    cv2.imshow('sent image', frame)
    frameStr = cv2.imencode('.jpg', frame)[1].tostring()
    print(len(frameStr))
    sock.sendto(frameStr, (HOST, PORT))
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break #die on q