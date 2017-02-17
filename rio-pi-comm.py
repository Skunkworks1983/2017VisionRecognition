import socket, sys, os

recv_ip = ""
send_ip = "10.19.83.41"
port = 8888

msg_len = 1024

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM);
sock.bind((recv_ip, port))

while 
    data, address = sock.recvfrom(msg_len);

    if(data != ""):
        if(data == "shutdown"):
            os.system("sudo shutdown -h now")
