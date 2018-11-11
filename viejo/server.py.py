#https://www.reddit.com/r/flask/comments/36ngb7/af_how_can_i_interrupt_an_infinite_while_loop_on/
#http://code.activestate.com/recipes/578247-basic-threaded-python-tcp-server/
#https://stackoverflow.com/questions/11523918/python-start-a-function-at-given-time  A ESTE LO TENGO QUE ANALIZAR
import time
from datetime import datetime
#from threading import Thread, Event
#import socket
import sys
import sys
import traceback
import time



---------routes-----------------



'''
import socket
import sys
soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = "127.0.0.1"
port = 8888

try:
    soc.connect((host, port))
except:
    print("Connection error")
    sys.exit()
'''


-------------------------------





'''
class LoopThread(Thread):
    def __init__(self, stop_event, interrupt_event,continue_event):
        self.stop_event = stop_event
        self.interrupt_event = interrupt_event
        self.continue_event = continue_event
        Thread.__init__(self)

    def run(self):
        while True:

            if not self.stop_event.is_set() and not self.interrupt_event.is_set():
                self.loop_process()
            elif self.interrupt_event.is_set():
                self.interrupted_process()
                self.interrupt_event.clear()
            else:
                self.continue_event.wait()
                self.stop_event.clear()
                self.continue_event.clear()

    def loop_process(self):
        print("Processing!")
        time.sleep(3)

    def interrupted_process(self):
        print("Interrupted!")
        
STOP_EVENT = Event()
CONTINUE_EVENT = Event()
INTERRUPT_EVENT = Event()
thread = LoopThread(STOP_EVENT, INTERRUPT_EVENT, CONTINUE_EVENT)

def main():
    start_server()


def start_server():
    host = "127.0.0.1"
    port = 8888         # arbitrary non-privileged port

    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)   # SO_REUSEADDR flag tells the kernel to reuse a local socket in TIME_WAIT state, without waiting for its natural timeout to expire
    print("Socket created")

    try:
        soc.bind((host, port))
    except:
        print("Bind failed. Error : " + str(sys.exc_info()))
        sys.exit()

    soc.listen(5)       # queue up to 5 requests
    print("Socket now listening")

    # infinite loop- do not reset for every requests
    while True:
        connection, address = soc.accept()
        ip, port = str(address[0]), str(address[1])
        print("Connected with " + ip + ":" + port)

        try:
            Thread(target=client_thread, args=(connection, ip, port)).start()
        except:
            print("Thread did not start.")
            traceback.print_exc()

    soc.close()


def client_thread(connection, ip, port, max_buffer_size = 5120):
    is_active = True

    while is_active:
        client_input = receive_input(connection, max_buffer_size)

        if "--QUIT--" in client_input:
            print("Client is requesting to quit")
            connection.close()
            print("Connection " + ip + ":" + port + " closed")
            is_active = False
        else:
            print("Processed result: {}".format(client_input))
            connection.sendall("-".encode("utf8"))


def receive_input(connection, max_buffer_size):
    client_input = connection.recv(max_buffer_size)
    client_input_size = sys.getsizeof(client_input)

    if client_input_size > max_buffer_size:
        print("The input size is greater than expected {}".format(client_input_size))

    decoded_input = client_input.decode("utf8").rstrip()  # decode and strip end of line
    result = process_input(decoded_input)

    return result


def process_input(input_str):
    print("Processing the input received from client")
    if input_str == "banca":
        INTERRUPT_EVENT.set()
        return "se banco el proceso ameo"
    if input_str == "para":
        STOP_EVENT.set()
        return "se paro el proceso ameo"
    if input_str == "segui":
        CONTINUE_EVENT.set()
        return "salimooooo"
    return str(input_str).upper()

if __name__ == '__main__':
    thread.start()
    main()

con el interrupt:event lo interrumpo y despues sigue el processing, parece copado, puede andar, (meto ahi lo de xbee?)

update 25/7: por defecto el thread.start() llama al run del thread y queda en ese while. con el continue meto un wait
que lo que hace es esperar a que ese valor sea seteado. una vez seteado sigue el thread. podemos tener varios hilos con
esto, tener varios dando vuelta encargandose de una cosa cada uno (tipo luz, temp, etc) y con los distintos events ir
tratando cada uno 


'''
