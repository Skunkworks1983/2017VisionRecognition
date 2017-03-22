import socket

HOST = ""
PORT = 5800

try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print('Socket created!')
except:
    print('Socket creation fail!')
    
try:
    sock.bind((HOST, PORT))
    print('Bound!')
except:
    print('Bind failed.')

while True:
    data, addrs = sock.recvfrom(1024)
    
sock.close()