#  File that can send strings and recieve strings over UDP to test the riosocket.py module.

import riosocket

riosocket = riosocket.RioSocket()

def main():
    while True:
        riosocket.send('goal', True, .04)
        data = riosocket.recv()
        print(data)
