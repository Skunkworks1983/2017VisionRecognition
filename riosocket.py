#RioSocket.py
#Formats data to be sent of to cMessenger
import socket, os, threading

HOST = "10.19.83.2"
PORT = 5802 # TODO port cannot be hardcoded.
data = ''
shutdown = False

class cListen (threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.MSG_LEN = 1024
        
    def run(self):
        global data
        global shutdown
        while data is not 'shutdown' and not shutdown: 
            try: data, addrs = self.sock.recvfrom(self.MSG_LEN)
            except: pass

class RioSocket():
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        thread = cListen()
        thread.start()
        
    def send(self, type, isFound, x, y=0):
        type = 1 if type == "goal" else 0
        isFound = 1 if isFound else 0
        message = str(type) + " " + str(isFound) + " " + str(x) + " " + str(y)
        try: self.sock.sendto(message, (HOST, PORT))
        except: pass

    def recv(self):
        global data
        global shutdown
        if not shutdown: 
            return data
        else:
            return 'shutdown'
        
    def shutdown(self):
        global shutdown
        shutdown = True
