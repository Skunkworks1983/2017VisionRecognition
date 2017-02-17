#RioSocket.py
#Formats data to be sent of to cMessenger
import socket, os

HOST = "10.19.83.2"
PORT = 5802 # TODO port cannot be hardcoded.

MSG_LEN = 1024

class RioSocket():
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
    def send(self, type, isFound, x, y=0):
        type = 1 if type == "goal" else 0
        isFound = 1 if isFound else 0
        message = str(type) + " " + str(isFound) + " " + str(x) + " " + str(y)
        self.sock.sendto(message, (HOST, PORT))

    def recv(self):
        return self.sock.recvfrom(MSG_LEN)
   
    def shutdown():
        #eric, put your shutdown stuff in here

        os.system("sudo shutdown -h now")
