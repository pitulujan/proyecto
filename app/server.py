from datetime import timedelta, datetime, date
from app.configuracion_scheduler import config_scheduler
from app.models import User, Devices, Log,Scheduled_events,Sensors,Log
from app import db
from flask import jsonify
from threading import Thread
import socket
import sys
import traceback
import time
import ast
import random 
import time

Current_state_dic_temp= {}
Current_state_dic_rooms ={}
Current_sensors ={}
Sensors_state={}
New_devices={}
New_sensors={}
Presence={}
Sent_messages={}
flag= False
new_dev_mac=''
new_dev_mac_enabled=False

seq_num = 0  #Este es para verificar que la respuesta recibida fue la del mensaje enviado random.randint(0,256)

def start_client():
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = "127.0.0.1"
    port = 9999

    try:
        soc.connect((host, port))
    except:
        print("Connection error")
        #sys.exit()
        return "Connection error"

    return soc 

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

    soc.listen(1)       # queue up to 5 requests
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

        print("Processed result: {}".format(client_input))
        connection.sendall("ok".encode("ascii","ignore"))

def receive_input(connection, max_buffer_size):

    client_input = connection.recv(max_buffer_size)
    client_input_size = sys.getsizeof(client_input)

    if client_input_size > max_buffer_size:
        print("The input size is greater than expected {}".format(client_input_size))

    decoded_input = client_input.decode("ascii","ignore")  # decode and strip end of line
    result = process_input(decoded_input)

    return result

def process_input(input_str):
    global Current_sensors
    global flag
    global new_dev_mac
    global new_dev_mac_enabled
    global New_devices
    global Sensors_state
    global Sent_messages
    print("Processing the input received from client")
    input_str=str(input_str).replace(chr(0), '')
    
    try:
        print('pitu-->', type(input_str))
        message = ast.literal_eval(input_str)
    
        try:
            print('pitu-->',message.keys(), message)
            if 'sensor_update' in message.keys():

                mac_address=message['sensor_update']['mac_address']

                if message['sensor_update']['presence_state']==1:
                    presence_state = True
                else:
                    presence_state = False

                if message['sensor_update']['battery']==1:
                    battery = True
                else:
                    battery = False

                if message['sensor_update']['battery_state'] == 1:
                    battery_state = True
                else:
                    battery_state = False

                temp_state = int( message['sensor_update']['temp_state'])

                new = True
                for location in Current_sensors:
                    if Current_sensors[location]['mac_address']== mac_address:
                        new = False 
                        Current_sensors[location]['presence_state'] = presence_state
                        Current_sensors[location]['battery'] = battery 
                        Current_sensors[location]['battery_state'] = battery_state
                        Current_sensors[location]['temp_state'] = temp_state
                        Current_sensors[location]['online'] = True
                        Sensors_state[mac_address]=datetime.now()

                if new and mac_address not in New_sensors.keys() :
                    New_sensors[mac_address] = {'presence_state':presence_state,'online':True,'battery': battery, 'battery_state':battery_state, 'temp_state': temp_state, 'mac_address':mac_address}

                    flag = True 
                    new_dev_mac = list(New_devices.keys()) + list(New_sensors.keys())
                    new_dev_mac_enabled = True

                message = ' 5 '+str(1)
                message=str(len(message)+1)+message
                send_socket(message)        
            elif 'tx_ok' in message.keys():
                mac_address = message['tx_ok']['mac_address']
                seq_number = message['tx_ok']['seq_number']
                del Sent_messages[seq_number]

                message = ' 5 '+str(1)
                message=str(len(message)+1)+message
                send_socket(message)
            else:
                print(message)
                message = ' 5 '+str(0)
                message=str(len(message)+1)+message
                send_socket(message)
                return str(input_str)
        except:
                message = ' 5 '+str(0)
                message=str(len(message)+1)+message
                send_socket(message)

    except  Exception as e:
        print(e)
        message = ' 6'
        message=str(len(message)+1)+message
        send_socket(message) 
     
        print(input_str)
        return str(0)

def remove_sens(user,mac_address):
    global Current_sensors
    sensor_to_delete = Sensors.query.filter_by(mac_address=mac_address).first()
    
    sensor_location = sensor_to_delete.location
    db.session.delete(sensor_to_delete)

    description= "Sensor has been removed from "+sensor_location
    log_entry = Log(user=user,timestamp=datetime.now().strftime("%Y/%m/%d %H:%M:%S"),description = description)
    db.session.add(log_entry)
    
    del Current_sensors[sensor_location]
    db.session.commit()
    scheduler.remove_job(mac_address)
    return 'The sensor was successfully removed from '+sensor_location

def remove_dev(user,location_str_id):

    location = ' '.join(location_str_id.split('/')[0].split('-'))
    str_id=' '.join(location_str_id.split('/')[1].split('.'))
        

    global Current_state_dic_rooms
    device_to_remove=Devices.query.filter_by(location=location,str_id=str_id).first()
    
    scheduled_events_to_del=Scheduled_events.query.filter_by(location=location,str_id=str_id)
    pids=[]
    for pid in scheduled_events_to_del:
        pids.append(pid.pid)
    
    if len(pids)!=0:
        delete_scheduled_event(pids)
        db.session.delete(scheduled_events_to_del)

    description= "Device "+str_id+" has been removed from "+location
    log_entry = Log(user=user,timestamp=datetime.now().strftime("%Y/%m/%d %H:%M:%S"),description = description)
    db.session.add(log_entry)
    
    db.session.delete(device_to_remove)
    del Current_state_dic_rooms[location][str_id]
    if len(Current_state_dic_rooms[location]) == 0:
        del Current_state_dic_rooms[location]
    db.session.commit()
    return 'Device '+str_id+' was successfully removed from '+location
              

def tick():
    print('Tick! The time is: %s' % datetime.now())
scheduler = config_scheduler()
scheduler.add_job(tick, 'interval', seconds=300,id='basic',replace_existing=True)
scheduler.add_job(start_server,  'date', run_date=datetime.now(), id='basic_server',replace_existing=True)

scheduler.start()

def get_activity_log():
    return Log.query.all()

def get_initial_values():

    global Current_state_dic_temp
    global Current_state_dic_rooms
    query_devices=Devices.query.all()
    for location in query_devices:
        if location.location in Current_state_dic_rooms.keys():
            Current_state_dic_rooms[location.location][location.str_id]={'dev_type' : location.dev_type, 'State': location.state , 'set_point' : location.set_point, 'user_perm' : location.user_perm, 'mac_address':location.mac_address,'temp_dev':location.temp_device,'online': False}
        else:
            Current_state_dic_rooms[location.location] = {location.str_id:{'dev_type' : location.dev_type, 'State': location.state , 'set_point' : location.set_point, 'user_perm' : location.user_perm, 'mac_address':location.mac_address,'temp_dev':location.temp_device,'online': False}}
    #query_temp=Temperature.query.first()
    #Current_state_dic_temp={ 'State' : query_temp.state,'Set_Point' : query_temp.set_point, 'Current_value': 25} # Hay que ver como medimos el current value y lo agregamos

    query_sensors = Sensors.query.all()

    for sensor in query_sensors:
        Current_sensors[sensor.location]={'presence_state':False,'online':False, 'mac_address':sensor.mac_address,'battery': sensor.battery, 'battery_state':False, 'temp_state': 20}
        Sensors_state[sensor.mac_address]=sensor.last_update



    #print(Current_state_dic_rooms)
    print(Current_sensors)
    return

def set_temp(state,set_point,user):#Aca no tengo en cuenta si hay mas de un sector en las temperaturas, si los hay en el futuro hay que tocar esto
    global Current_state_dic_rooms
    global Sent_messages

    query_temp=Devices.query.filter_by(temp_device=True).first()

    mac_address=query_temp.mac_address

    
    #seq_num=take_action(mac_address,state,set_point)
    ans=take_action(mac_address,state,set_point)
    
    if type(ans)==int:
        count = 0
        online = True
        print(ans)
        while True:
            if str(ans) in Sent_messages.keys():
                count+=1
                time.sleep(0.2)
            else:
                break
            if count == 5:
                online = False
                break

        if online:
            Current_state_dic_rooms['Temperature']['Temperature']['State'] = state
            query_temp.state=state

            if not Current_state_dic_rooms['Temperature']['Temperature']['dev_type']:
                Current_state_dic_rooms['Temperature']['Temperature']['set_point'] = set_point
                query_devices.set_point =set_point
            db.session.add(query_temp)
            db.session.commit()
            return jsonify({'status':200})
        else:
            print('la rompi devolviendo')
            return jsonify({'status':400, 'str_id':'Temperature','location':'Temperature'})
    else:
        print('que onda?')
        return jsonify({'status':400, 'str_id':'Temperature','location':'Temperature'})



def set_device(location, str_id,state,set_point):
    global Current_state_dic_rooms
    global Sent_messages
    
    query_devices=Devices.query.filter_by(location=location,str_id=str_id).first()


    mac_address= query_devices.mac_address


    ans=take_action(mac_address,state,set_point)
    
    if type(ans)==int:
        count = 0
        online = True
        print(ans)
        while True:
            if str(ans) in Sent_messages.keys():
                count+=1
                time.sleep(0.2)
            else:
                break
            if count == 5:
                online = False
                break

        if online:
            Current_state_dic_rooms[location][str_id]['State'] = state
            query_devices.state=state

            if not Current_state_dic_rooms[location][str_id]['dev_type']:
                Current_state_dic_rooms[location][str_id]['set_point'] = set_point
                query_devices.set_point =set_point
            db.session.add(query_devices)
            db.session.commit()
            return jsonify({'status':200})
        else:
            print('la rompi devolviendo')
            return jsonify({'status':400, 'str_id':str_id,'location':location})
    else:
        return jsonify({'status':400, 'str_id':str_id,'location':location})


def get_temp_state():
    global Current_sensors
    global Current_state_dic_rooms
    temp_dev=Devices.query.filter_by(temp_device=True).first()
    if temp_dev !=None:
        aux_temp=0
        active=False
        count=0

        for key in Current_sensors.keys():
            if Current_sensors[key]['online'] == True: # --> hacemos un promedio de los sensores que esten activos
                active=True
                aux_temp+= Current_sensors[key]['temp_state']
                count+=1

        if active:
            tem_prom=int(aux_temp/count )
        else:
            tem_prom='-'


        return { 'State' : temp_dev.state,'Set_Point' : temp_dev.set_point, 'Current_value': tem_prom, 'online': Current_state_dic_rooms['Temperature']['Temperature']['online']} 
    else:
        return None 

def get_devices():
    return Current_state_dic_rooms #--> que se la arrgle routes

def get_scheduled_events(*args):

    if args:
        query_scheduled = Scheduled_events.query.filter_by(str_id=args[0],location=args[1]).all()
    else:
        query_scheduled = Scheduled_events.query.all()
    
    return query_scheduled

def alarm(state,set_point,event_type,id_job,mac_address):

    if event_type == 'date':
        delete_scheduled_event(id_job)

        #aca falta llamar al cliente para que mande el mensaje al programa en C
    if state == True:
        state=1
    else:
        state=0

    message = ' 1 '+mac_address+' '+state+' '+set_point
    message=str(len(message)+1)+message
    send_socket(message)
    print(state,set_point,event_type,id_job)

def schedule_event(user,str_id,location,start_date,pidd,param_state,param_set_point,args=[], day_of_week=[]):
    str_id=str_id.replace('_',' ')
    try:
        if len(start_date.split(':'))==3:
            start_date=start_date[:-3]
        date_date=start_date.replace('T',' ')+':00'
    except:
        ans={'status':400,'pid':'','error_message': 'Date/hour needed'}

        return jsonify(ans)

    #print(pidd)
    check_date=check_days(date_date,day_of_week,str_id,location,pidd)
    reschedule=False

    if pidd != 'None' and check_date == False:
        event_to_reschedule = Scheduled_events.query.filter_by(pid=pidd).first()
        reschedule = True
        db.session.delete(event_to_reschedule)
        db.session.commit()


    if check_date == True:

        ans={'status':400,'pid':'','error_message': 'Try picking another day/hour for this device'}

        return jsonify(ans)

    else:

        if param_state == 'On':
            param_state=True
        else:
            param_state=False
        dat=datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        id_job=user+'_'+dat

        date=start_date.split('T')[0]
        try:
            hour= start_date.split('T')[1].split(':')[0]
            minute= start_date.split('T')[1].split(':')[1]
        except:
            ans={'status':400,'pid':'','error_message': 'Date/hour needed'}

            return jsonify(ans)

        getting_mac = Devices.query.filter_by(location=location,str_id=str_id).first()

        if len(day_of_week)!=0:

            scheduler.add_job(alarm, 'date', run_date=date_date, args=[param_state,param_set_point,'cron',id_job,getting_mac.mac_address],id=id_job)
            scheduler.add_job(alarm, 'cron', start_date=date, day_of_week=','.join(day_of_week), hour=hour, minute=minute , args=[param_state,param_set_point,'cron',id_job,getting_mac.mac_address],id=id_job+'_cron') #para que lo haga ese dia y despues repita
            
            days={'0':'Mon','1':'Tue','2':'Wed','3':'Thu','4':'Fri','5':'Sat','6':'Sun'}
            cron_days=[]   
            for day in day_of_week:
                cron_days.append(days[day])

            event_to_schedule= Scheduled_events(user=user,str_id=str_id,location=location,event_date=date_date,event_type='cron',event_cron='.'.join(cron_days),event_param_state=param_state,event_param_setpoint=param_set_point, pid=id_job+'_cron')
            
            hour_minute = hour+':'+minute

            ans={'status':200,'pid':id_job+'_cron','date':date_date,'hour':hour_minute,'type':'cron','cron_days':cron_days,'location':location,'str_id':str_id,'reschedule': reschedule,'old_pid':pidd,'param_state':param_state,'param_set_point':param_set_point}
            

        else:

            scheduler.add_job(alarm, 'date', run_date=date_date, args=[param_state,param_set_point,'date',id_job,getting_mac.mac_address],id=id_job)
            event_to_schedule= Scheduled_events(user=user,str_id=str_id,location=location,event_date=date_date,event_type='date',event_cron=None,event_param_state=param_state,event_param_setpoint=param_set_point, pid=id_job)
            ans={'status':200,'pid':id_job,'date':date_date,'hour':hour,'type':'date','cron_days':None,'location':location,'str_id':str_id,'reschedule':reschedule,'old_pid':pidd,'param_state':param_state,'param_set_point':param_set_point}

        description= "An event for "+str_id+" in "+location+" has been set"
        log_entry = Log(user=user,timestamp=datetime.now().strftime("%Y/%m/%d %H:%M:%S"),description = description)
        db.session.add(log_entry)
        db.session.add(event_to_schedule)
        db.session.commit()

        
        return jsonify(ans)

def check_days(date,day_of_week,str_id,location,pidd):

    #aca hay primero que ver si alguna tupla str_id y location coinciden, si no es asi, return false, sino ahi ver len(day_of_week)

    events = get_scheduled_events(str_id,location)  #--> Ojo que esto puede ser una lista 
    flag = False
    if events == None:
        return False   
    else:
        
        for scheduled_event in events: 
            if scheduled_event.event_type == 'date' and len(day_of_week)==0 and scheduled_event.event_date == date: #len()==0 implica date y no cron(date)
                if pidd != scheduled_event.pid:
                    flag=True 
                    break 
            elif scheduled_event.event_type == 'cron' and len(day_of_week)!=0 and scheduled_event.event_date.split(' ')[1] == date.split(' ')[1]: #si ambos son cron y la hora coincide, checkeo dias
                for day in scheduled_event.event_cron.split('.'):
                    if day in day_of_week:
                        if pidd != scheduled_event.pid:
                            flag=True
                            break


            elif scheduled_event.event_date.split(' ')[1] == date.split(' ')[1]: #solo entro en caso de que matcheen las horas



                if scheduled_event.event_type == 'cron':
                    days={'Mon':'0','Tue':'1','Wed':'2','Thu':'3','Fri':'4','Sat':'5','Sun':'6'}
                    aux=[]
                    for day in scheduled_event.event_cron.split('.'):
                        aux.append(days[day])
                    d=datetime.strptime(scheduled_event.event_date.split(' ')[0],'%Y-%m-%d').date() #dia minimo a partir del cual el cron empieza a funcionar
                    weekday=list(map(int,aux)) #paso la lista de strings a lista de ints
                    dia_que_quiero =datetime.strptime(date.split(' ')[0],'%Y-%m-%d').date()
                else:
                    #mismo que el anterior solo que se invierte el orden de dia que quiero y dia que tengo 
                    d=datetime.strptime(date.split(' ')[0],'%Y-%m-%d').date() #dia minimo a partir del cual el cron empieza a funcionar
                    weekday=list(map(int,day_of_week)) #paso la lista de strings a lista de ints
                    dia_que_quiero =datetime.strptime(scheduled_event.event_date.split(' ')[0],'%Y-%m-%d').date()



                def next_weekday(d, weekday_list):

                    days=[]
                    for weekday in weekday_list:
                        days_ahead = weekday - d.weekday()
                        if days_ahead <= 0: # Target day already happened this week
                            days_ahead += 7
                        days.append(d + timedelta(days_ahead))
                    return days
                array_dates = next_weekday(d,weekday)

                #print(array_dates)

                for datee in array_dates:
                    aux_date=datee
                    while aux_date <=dia_que_quiero:
                        if aux_date == dia_que_quiero:
                            if pidd != scheduled_event.pid:
                                #print('hijo de mill',aux_date)
                                flag = True
                                break
                        else:
                            aux_date+=timedelta(days=7)

    return flag

def delete_scheduled_event(user,id_event):

    if type(id_event)==list: #Esto es por si elimino un usuario para eliminar todos los eventos que tenia schedulizados
        for pid in id_event:
            scheduler.remove_job(pid)
    else:
        aux=id_event.split('_')
        if 'cron' in aux:
            aux.remove('cron')
            scheduler.remove_job(id_event)
            
            try:
                scheduler.remove_job('_'.join(aux)) 
            except Exception as e:
                pass
            
            

        else:
            try:
                scheduler.remove_job(id_event)
            except Exception as e:
                pass
        event = Scheduled_events.query.filter_by(pid=id_event).first()

        description= "An event for "+event.str_id+" in "+event.location+" has been deleted"
        log_entry = Log(user=user,timestamp=datetime.now().strftime("%Y/%m/%d %H:%M:%S"),description = description)
        db.session.add(log_entry)
        db.session.delete(event)
        db.session.commit()

    return

def get_new_device():
    return flag,new_dev_mac,new_dev_mac_enabled

def edit_device_server(old_location,new_location,old_str_id,new_str_id,state,set_point,mac_address):
    global Current_rooms

    device_to_edit = Devices.query.filter_by(mac_address=mac_address).first()
    trying_to_change = Devices.query.filter_by(location=new_location,str_id=new_str_id).first()

    if trying_to_change != None:
        message = "There's already a device called "+new_str_id+" in "+new_location
        return {'status': 400, 'message' : message}
    else:

        if state == 'On':
            state = True
        else:
            state = False 
        device_to_edit.location = new_location
        device_to_edit.str_id= new_str_id
        device_to_edit.state= state
        device_to_edit.set_point = set_point
        #device_to_add = Devices(user_perm=device_to_edit.user_perm,str_id=new_str_id,location=new_location,dev_type=device_to_edit.dev_type,state=state,set_point=set_point,new_device=False,mac_address=mac_address)

        if new_location not in Current_state_dic_rooms.keys():
            Current_state_dic_rooms[new_location] = {new_str_id:{'dev_type' : device_to_edit.dev_type, 'State': state , 'set_point' : set_point, 'user_perm' : device_to_edit.user_perm,'mac_address': mac_address}}
            #Current_rooms[new_location]=True
        else:
            if new_str_id not in Current_state_dic_rooms[new_location]:
                Current_state_dic_rooms[new_location][new_str_id] = {'dev_type' : device_to_edit.dev_type, 'State': state , 'set_point' : set_point, 'user_perm' : device_to_edit.user_perm, 'mac_address': mac_address}
        
        
        Current_state_dic_rooms[old_location].pop(old_str_id)
        if (len(Current_state_dic_rooms[old_location])==0):
            Current_state_dic_rooms.pop(old_location)
        
        #db.session.delete(device_to_edit)
        db.session.commit()
        #db.session.add(device_to_add)device_to_add = Devices(user_perm=device_to_edit.user_perm,str_id=new_str_id,location=new_location,dev_type=device_to_edit.dev_type,state=state,set_point=set_point,new_device=False,mac_address=mac_address)
        #db.session.commit()

        return {'status': 200, 'message' : "Device "+new_str_id+" has been successfully added to "+new_location}

def edit_sensor_server(old_location,new_location,mac_address):
    global Current_sensors

    if new_location in Current_sensors.keys():
        message = "There's already a sensor in "+new_location
        return {'status': 400, 'message' : message}
        
    sensor_to_edit = Sensors.query.filter_by(mac_address=mac_address).first()

    sensor_to_edit.location=new_location

    db.session.add(sensor_to_edit)
    
    Current_sensors[new_location] = Current_sensors[old_location]
    del Current_sensors[old_location]

    db.session.commit()

    return {'status': 200, 'message' : "Sensor has been successfully moved from "+old_location+" to "+new_location}

def add_new_device_server(user,location,str_id,state,set_point,mac_address,temp_dev):
    global flag
    global new_dev_mac
    global Current_rooms
    global New_sensors

    
    trying_to_add = Devices.query.filter_by(location=location,str_id=str_id).first()

    if trying_to_add != None:
        message = "There's already a device called "+str_id+" in "+location
        return {'status': 400, 'message' : message}
    else:
        if state == 'On':
            state = True
        else:
            state = False
        if temp_dev =='True':
            temp_dev=True
        else:
            temp_dev=False

        device_to_add = Devices(user_perm=New_devices[mac_address]['user_perm'],str_id=str_id,location=location,dev_type=New_devices[mac_address]['dev_type'],state=state,set_point=set_point,temp_device=temp_dev,mac_address=mac_address)
        

        if location not in Current_state_dic_rooms.keys():
            Current_state_dic_rooms[location] = {str_id:{'dev_type' : New_devices[mac_address]['dev_type'], 'State': state , 'set_point' : set_point, 'user_perm' : New_devices[mac_address]['user_perm'],'mac_address': mac_address,'temp_dev':temp_dev,'online':True}}
           # Current_rooms[location]=False
        else:
            if str_id not in Current_state_dic_rooms[location]:
                Current_state_dic_rooms[location][str_id] = {'dev_type' : New_devices[mac_address]['dev_type'], 'State': state , 'set_point' : set_point, 'user_perm' : New_devices[mac_address]['user_perm'], 'mac_address': mac_address,'temp_dev':temp_dev,'online':True}
        
        description= "New device "+str_id+" has been added to "+location
        log_entry = Log(user=user,timestamp=datetime.now().strftime("%Y/%m/%d %H:%M:%S"),description = description)
        db.session.add(log_entry)
        
        db.session.add(device_to_add)
        db.session.commit()
        New_devices.pop(mac_address)
        new_dev_mac = list(New_devices.keys()) + list(New_sensors.keys())
        if len(new_dev_mac)==0:  
            #print('flag server entro bien ')
            flag = False
        return {'status': 200, 'message' : "Device "+str_id+" has been successfully added to "+location , 'ndkl':len(new_dev_mac)}

def add_new_sensor_server(user,location,mac_address,battery,presence_state,online,battery_state,temp_state):

    if presence_state == 'True':
        presence_state = True
    else:
        presence_state =False
        
    
    if online == 'True':
        online= True 
    else:
        online = False

    if battery =='True':
        battery=True
    else:
        battery=False

    if battery_state == 'True':
        battery_state = True
    else:
        battery_state=False

    global flag
    global new_dev_mac
    global New_sensors
    global Current_sensors
    
    if location in Current_sensors.keys():
        return {'status': 400, 'message' : 'There is already a sensor with that name in that room'}
    else:
        Current_sensors[location]={'presence_state':presence_state,'online':online, 'mac_address':mac_address,'battery': battery, 'battery_state':battery_state, 'temp_state': int(temp_state)}

    sensor_to_add = Sensors(location=location,battery=battery,mac_address=mac_address)
    description= "New sensor has been added to "+location
    log_entry = Log(user=user,timestamp=datetime.now().strftime("%Y/%m/%d %H:%M:%S"),description = description)
    db.session.add(log_entry)
    db.session.add(sensor_to_add)
    db.session.commit()
    Sensors_state[mac_address]=datetime.now()
    scheduler.add_job(check_sensor_state, 'interval', seconds=2,args=[mac_address],id=mac_address)
    New_sensors.pop(mac_address)
    new_dev_mac = list(New_devices.keys()) + list(New_sensors.keys())
    if len(new_dev_mac)==0:  
        #print('flag server entro bien ')
        flag = False
    return {'status': 200, 'message' : "Sensor has been successfully added to "+location , 'ndkl':len(new_dev_mac)}

def check_sensor_state(mac_address):
    global Current_sensors
    global Sensors_state

    #print('hola, estoy checkeando si el sensor '+mac_address+" está vivito y coleando")
    for sensor in Current_sensors:
        if mac_address == Current_sensors[sensor]['mac_address']:
            if round((datetime.now()-Sensors_state[mac_address]).total_seconds()/60)<1:
                Current_sensors[sensor]['online']= True
            else:
                Current_sensors[sensor]['online']=False

    return

def get_new_devices():

    if len(New_devices.keys())!=0:
        return New_devices
    else:
        return None

def get_temp_device():
    temp_device= Devices.query.filter_by(temp_device=True).first()
    return temp_device

def get_current_sensors():
    global Current_sensors
    return Current_sensors

def generate_dummy_device_test(dev_type):
    if dev_type == 'True':
        dev_type = True
    else:
        dev_type = False 
    ## Agrego un dispositivo al diccionario simplemente para probar el metodo 'Add device' simulando un nuevo dispositivo que se incorpora al sistema
    global flag
    global new_dev_mac
    global new_dev_mac_enabled
    global New_sensors
    
    if '08:00:27:60:03:90' not in New_devices.keys():
        New_devices['08:00:27:60:03:90'] = {'dev_type' : dev_type , 'State': False , 'set_point' : None, 'user_perm' : False , 'new_device': True, 'mac_address':'08:00:27:60:03:90'}
    else:
        
        New_devices['08:00:27:60:03:9'+str(len(New_devices.keys()))] = {'dev_type' : dev_type , 'State': False , 'set_point' : None, 'user_perm' : False , 'new_device': True, 'mac_address':'08:00:27:60:03:9'+str(len(New_devices.keys()))} 

    #print(New_devices)
    flag = True 
    new_dev_mac = list(New_devices.keys()) + list(New_sensors.keys())
    new_dev_mac_enabled = True
    return

def generate_dummy_sensor_test(presence_state,online,battery,battery_state,temp_state):

   
    if presence_state == 'True':
        presence_state = True
    else:
        presence_state =False
        
    
    if online == 'True':
        online= True 
    else:
        online = False

    if battery =='True':
        battery=True
    else:
        battery=False

    if battery_state == 'True':
        battery_state = True
    else:
        battery_state=False 
    ## Agrego un dispositivo al diccionario simplemente para probar el metodo 'Add device' simulando un nuevo dispositivo que se incorpora al sistema
    global flag
    global new_dev_mac
    global new_dev_mac_enabled
    global New_devices
    
    if '08:00:27:60:04:00' not in New_sensors.keys():
        New_sensors['08:00:27:60:04:00'] = {'presence_state':presence_state,'online':online,'battery': battery, 'battery_state':battery_state, 'temp_state': int(temp_state), 'mac_address':'08:00:27:60:04:00'}
    else:
        
        New_sensors['08:00:27:60:04:0'+str(len(New_sensors.keys()))] = {'presence_state':presence_state,'online':online,'battery': battery, 'battery_state':battery_state, 'temp_state': temp_state, 'mac_address':'08:00:27:60:04:0'+str(len(New_sensors.keys()))} 

    #print(New_devices)
    flag = True 
    new_dev_mac = list(New_devices.keys()) + list(New_sensors.keys())
    new_dev_mac_enabled = True
    return

def get_new_sensors():
    if len(New_sensors.keys())!=0:
        return New_sensors
    else:
        return None

def disable_new_dev_mac():
    global new_dev_mac_enabled
    new_dev_mac_enabled = False
    return

def send_socket(text):
    global soc 

    try:
        soc.sendall(text.encode("ascii","ignore"))
        if soc.recv(5120).decode("ascii","ignore") == "ok":
            print('recieved akn from server')        # null operation

    except Exception as e:
        soc=start_client()
        if type(soc)!= str:
            start = time.perf_counter()
            soc.sendall(text.encode("ascii","ignore"))
            print ('time taken ', time.perf_counter()-start ,' seconds')
            if soc.recv(5120).decode("ascii","ignore") == "ok":
                print('recieved akn from server')        # null operation
        else:
            return soc 
    return None 

def take_action(mac_address,state,set_point):
    global Sent_messages
    if state == True:
        state=1
    else:
        state=0

    seq_number = random.randint(0,256)

    message = ' 1 '+mac_address+' '+str(state)+' '+str(set_point)
    message=str(len(message)+1)+message

    ans=send_socket(message)
    print('y aca?',ans)
    if ans == None:
        #Sent_messages[str(seq_number)]={'mac_address': mac_address, 'state': state,'set_point':set_point}
        print(Sent_messages)
        return seq_number
    else:
        return ans 




            


