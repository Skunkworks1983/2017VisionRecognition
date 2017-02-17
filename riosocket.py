#RioSocket.py
#Formats data to be sent of to cMessenger
import socket

HOST = "10.19.83.101"
PORT = 8888

class RioSocket():
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
    def send(self, type, isFound, x, y=0):
        first = 1 if type == "goal" else 0
	isFound = 1 if isFound else 0
        message = str(type) + " " + str(isFound) + " " + str(x) + " " + str(y)
        self.sock.sendto(message, (HOST, PORT))
            
