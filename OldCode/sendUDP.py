import socket, sys

HOST = 'localhost'
PORT = 5802


try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print('Socket created!')
except:
    print('Socket creation fail!')   
   
while(True):
    print(sys.argv[1])
    sock.sendto(sys.argv[1], (HOST, PORT))