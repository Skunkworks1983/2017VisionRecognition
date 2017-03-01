import numpy as np
import socket, cv2, time

HOST = ""
PORT = 5802

try:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print('Socket created!')
except:
    print('Socket creation fail!')
    
try:
    s.bind((HOST, PORT))
    print('Bound!')
except:
    print 'Bind failed.'

while True:
    data, addrs = s.recvfrom(7000)
    
    nparr = np.fromstring(data, np.uint8)
    
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    frame = cv2.resize(frame, (0,0), fx=5, fy=5)
    
    cv2.imshow('received image', frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break #die on q
    
s.close()