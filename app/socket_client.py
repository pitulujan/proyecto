#http://code.activestate.com/recipes/578247-basic-threaded-python-tcp-server/
import socket
import sys

def start_client():
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = "127.0.0.1"
    port = 9999

    try:
        soc.connect((host, port))
    except:
        print("Connection error")
        sys.exit()

    return soc 
