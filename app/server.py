#https://www.reddit.com/r/flask/comments/36ngb7/af_how_can_i_interrupt_an_infinite_while_loop_on/
#http://code.activestate.com/recipes/578247-basic-threaded-python-tcp-server/
#https://stackoverflow.com/questions/11523918/python-start-a-function-at-given-time  A ESTE LO TENGO QUE ANALIZAR
import time
from datetime import datetime
#from threading import Thread, Event
#import socket
import sys
import traceback
import sqlite3
from app.configuracion_scheduler import config_scheduler

from app.models import User, User_Light_State,User_Temperature_State,Scheduled_events,Current_Light_State,Current_Temperature_State
from app import db



route = '/home/pitu/proyecto/app.db'

Current_state_dic= {'Temperature':        { 'State' : False,'Set_Point' : 12.0},
                    'Lights' : { 'Cocina': { 'State' : False,'Intensity' : 10.0},
                                'Living': { 'State' : False,'Intensity' : 10.0},
                                'Patio':  { 'State' : False,'Intensity' : 10.0}}

                    }

def tick():
    print('Tick! The time is: %s' % datetime.now())
scheduler = config_scheduler()
scheduler.add_job(tick, 'interval', seconds=20,id='basic',replace_existing=True)
#scheduler.start()

def get_initial_values():

    query_lights=Current_Light_State.query.all()
    for place in query_lights:
        Current_state_dic['Lights'][place.str_id]['State']=place.light_state
        Current_state_dic['Lights'][place.str_id]['Intensity']=place.light_intensity

    query_temp=Current_Temperature_State.query.first() #Si hay mas temperaturas (mas sectores) cambiar el first por un all y sus respectivos cambios despues 
    Current_state_dic['Temperature']['State']=query_temp.temp_state
    Current_state_dic['Temperature']['Set_Point']=query_temp.temp_set_point

    print(Current_state_dic)
    return

def set_temp(state,setpoint,user):#Aca no tengo en cuenta si hay mas de un sector en las temperaturas, si los hay en el futuro hay que tocar esto
    
    query_temp=Current_Temperature_State.query.first()
    
    query_temp.temp_state = state
    query_temp.temp_set_point = setpoint
    query_temp.user = user
    query_temp.timestamp = datetime.now()

    db.session.add(query_temp)
    db.session.commit()



def set_light(state,user_id,*args):
    conn=sqlite3.connect(route, check_same_thread=False)
    co=conn.cursor()

    
    Current_state_dic['Set_Point_Light']['State']=state
    
    touple=(state,Current_state_dic['Set_Point_Light']['Intensity'],datetime.now(),user_id)
    tup=(state,Current_state_dic['Set_Point_Light']['Intensity'],1)
    if args:
        Current_state_dic['Set_Point_Light']['Intensity']=args[0]
        touple=(state,args[0],datetime.now(),user_id)
        tup=(state,args[0],1)

    sql = "UPDATE User__State SET light_state = ?,light_intensity = ?, timestamp = ? WHERE user_id= ?"
    co.execute(sql, touple)

    sql = "UPDATE Current__State SET light_state = ?,light_intensity = ? WHERE id=?"
    co.execute(sql,tup)

    conn.commit()
    conn.close()
    get_set_point_temp()
    return


def get_set_point_temp():
    print(Current_state_dic['Temperature']['Set_Point'])
    return Current_state_dic['Temperature']['Set_Point']

def get_light_state():
    print(Current_state_dic['Set_Point_Light']['State'])
    return Current_state_dic['Set_Point_Light']['State']
def get_set_point_light():
    print(Current_state_dic['Set_Point_Light']['Intensity'])
    return Current_state_dic['Set_Point_Light']['Intensity']

def get_current_temp():
    return 20

def schedule_event(user,function,atribute,type=None,run_date=None,args=[],start_date=None,end_date=None,interval=None):



    scheduler.add_job(alarm, 'date', run_date='2018-10-21 20:42:00', args=[datetime.now()],id='Pitu 5')

    scheduler.add_job(alarm, 'interval', seconds=5, start_date='2018-10-10 09:30:00', end_date='2019-06-15 11:00:00',args=[datetime.now()],id='Pitu1')




    return

def reschedule_event():
    pass

def delete_scheduled_event(id_event):

    scheduler.remove_job(id_event)

    return

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
