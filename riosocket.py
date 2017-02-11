#RioSocket.py
#Formats data to be sent of to cMessenger
import socket

HOST = "10.19.83.2"
PORT = 5802

class RioSocket():
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
    def send(self, type, x, y=0):
        type = 1 if type == "goal" else 0
        message = str(type) + " " + str(x) + " " + str(y)
        self.sock.sendto(message, (HOST, PORT))
   

