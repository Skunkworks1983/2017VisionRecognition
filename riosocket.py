#RioSocket.py
#Formats data to be sent of to cMessenger
import numpy as np
import socket, os, threading, cv2, time, logging

HOST = "10.19.83.2"
TURRETPORT = 5802 # TODO port cannot be hardcoded.
GEARPORT = 5800
DRIVERPORT = 5804
data = 'no data recieved yet'
shutdown = False

class cListen (threading.Thread):
    def __init__(self, port):
        threading.Thread.__init__(self)
        self.sock2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock2.bind(("", port))
        self.MSG_LEN = 1024
        logging.info('Initialized cListen.')
        
    def run(self):
        global data
        global shutdown
        while data is not 'shutdown' and not shutdown:
            data, addrs = self.sock2.recvfrom(self.MSG_LEN)

class RioSocket():
    def __init__(self, target):
        if target == 'gear': port = GEARPORT
        elif target == 'goal': port = TURRETPORT
        else: logging.critical('Unknown target type! Cannot send target pos data!')
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        thread = cListen(port)
        thread.start()
        
    def send(self, type, isFound, x, y=0):
        type = 1 if type == "goal" else 0
        isFound = 1 if isFound else 0
        message = str(type) + " " + str(isFound) + " " + str(x) + " " + str(y)
        try:
            self.sock.sendto(message, (HOST, port))
        except:
            pass
        
    def sendVid(self, frame):
        frame = cv2.resize(frame, (0,0), fx=0.2, fy=0.2)
        frame = frame[:,:,0]
        frameStr = cv2.imencode('.jpg', frame)[1].tostring()
        print(len(frameStr))
        self.sock.sendto(frameStr, (HOST, DRIVERPORT)) 

    def recv(self):
        global data
        global shutdown
        if not shutdown: 
            return data
        else:
            return 'shutdownq'
        
    def shutdown(self):
        global shutdown
        shutdown = True
