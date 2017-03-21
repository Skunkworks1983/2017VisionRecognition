import socket, sys, time

HOST = 'localhost'
PORT = 5800
msg = '' # Rio has not been enabled yet

try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print('Socket created!')
except:
    print('Socket creation fail!')

print(sys.argv[1])

while(True):
    sock.sendto(sys.argv[1], (HOST, PORT))
    time.sleep(1)
