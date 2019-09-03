from datetime import timedelta, datetime, date
from app.configuracion_scheduler import config_scheduler
from app.models import User, Devices, Log, Scheduled_events, Sensors, Log
from app import db, socketio,app
from flask import jsonify
from threading import Thread
import socket
import sys
import traceback
import time
import ast
import random
import time
from flask_socketio import send, emit
import paho.mqtt.client as mqtt
from threading import Thread
from flask_mail import Message
from app import mail


Current_state_dic_temp = {}
Current_state_dic_rooms = {}
Current_sensors = {}
mapping_macs = {}
Sensors_state = {}
New_devices = {}
New_sensors = {}
Presence = {}
Sent_messages = {}
flag = False
new_dev_mac = ""
new_dev_mac_enabled = False
low_baterry_not = False
Low_baterry_array = []
temp_hist={'state': 'off'}
mail_batery_flag={}
mail_sensor_flag = {}

seq_num = (
    0
)  # Este es para verificar que la respuesta recibida fue la del mensaje enviado random.randint(0,256)



def callback_mqtt(client, userdata, message):
    global flag
    #print("message received " ,str(message.payload.decode("utf-8")))
    #print("message topic=",message.topic)
    #print("message qos=",message.qos)
    #print("message retain flag=",message.retain)
    #print("message info=",message.info)
    #print("message state=",message.state)
    ##print(dir(message))

def info1_mqtt(client, userdata, message):
    global flag
    global new_dev_mac
    global new_dev_mac_enabled
    global New_devices
    global Sensors_state
    global Current_state_dic_rooms

    fallback = ast.literal_eval(str(message.payload.decode("utf-8")))['FallbackTopic'].split('/')[1]
    #print(fallback)
    new=True
    for location in Current_state_dic_rooms:
    
        for str_id in Current_state_dic_rooms[location]:
            
            if (Current_state_dic_rooms[location][str_id]["mac_address"] == fallback):
                
                new = False
                break


    if new and fallback not in New_devices.keys():
        
        New_devices[fallback] = {
            "presence_state": False,
            "dev_type": True,
            "State": False,
            "set_point": 0,
            "online": True,
            "tactil_switch": False,
            "handles": "[]",
            "mac_address": fallback,
        }

        flag = True
        new_dev_mac = list(New_devices.keys()) + list(New_sensors.keys())
        new_dev_mac_enabled = True
        #print('no entiendo')
        socketio.emit("new_dev_tobrowser",{"arrayToSendToBrowser": new_dev_mac},namespace="/test")

def add_switch_mqtt(client, userdata, message):
    global flag
    global new_dev_mac
    global new_dev_mac_enabled
    global New_devices
    global New_sensors
    global Sensors_state
    global Current_state_dic_rooms
    #print('kkkkkkkkkkkkkkkkkkkkkkkkkkk')
    fallback = ast.literal_eval(str(message.payload.decode("utf-8")))['FallbackTopic'].split('/')[1]
    new=True
    for location in Current_state_dic_rooms:
    
        for str_id in Current_state_dic_rooms[location]:
            
            if (Current_state_dic_rooms[location][str_id]["mac_address"] == fallback):
                
                new = False
                break


    if new and fallback not in New_devices.keys():
        
        New_devices[fallback] = {
            "presence_state": False,
            "dev_type": True,
            "State": False,
            "set_point": 0,
            "online": True,
            "tactil_switch": True,
            "handles": str([]),
            "temp_device": False,
            "mac_address" : fallback,
        }

        flag = True
        new_dev_mac = list(New_devices.keys()) + list(New_sensors.keys())
        new_dev_mac_enabled = True
        #print('no entiendo')
        socketio.emit("new_dev_tobrowser",{"arrayToSendToBrowser": new_dev_mac},namespace="/test")

def add_temp_mqtt(client, userdata, message):

    global Current_state_dic_rooms
    global mapping_macs


    

    temp_dev = Devices.query.filter_by(temp_device=True).first()
    if temp_dev == None:
        fallback = ast.literal_eval(str(message.payload.decode("utf-8")))['FallbackTopic'].split('/')[1]
        mapping_macs[fallback]={'location': "Temperature",'str_id':"Temperature",'handles':"[]"}

        scheduler.add_job(controlling_temp, "interval", seconds=30, args=[], id=str(fallback))

     
        device_to_add = Devices(
                user_perm=True,
                str_id="Temperature",
                location="Temperature",
                dev_type=False,
                state=False,
                set_point=15,
                temp_device=True,
                mac_address=fallback,
                tactil_switch = False,
                handles = "[]",
            )

        Current_state_dic_rooms["Temperature"] = {
                    "Temperature": {
                        "dev_type": False,
                        "State": False,
                        "set_point": 15,
                        "user_perm": True,
                        "mac_address": fallback,
                        "temp_dev": True,
                        "online": True,
                        "presence_state": False,
                        "tactil_switch" : False,
                        "handles" : "[]",
                    }
                }
        
        description = "Thermostat added successfully"
        log_entry = Log(
            user='Default',
            timestamp=datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            description=description,
        )
        db.session.add(log_entry)

        db.session.add(device_to_add)
        db.session.commit()
        socketio.emit("new_temp_success",{"arrayToSendToBrowser": True},namespace="/test")

def result_mqtt(client, userdata,message):
    print("message received " ,str(message.payload.decode("utf-8")))
    print("message topic=",message.topic)
    #print("message qos=",message.qos)
    #print("message retain flag=",message.retain)
    print("message info=",message.info)
    #print("message state=",message.state)
    #print('tuviejakkk')

def touch_switch_mqtt(client,userdata,message):

    fallback = ast.literal_eval(str(message.payload.decode("utf-8")))['FallbackTopic']
    #print(fallback,'--> TOGGLE')
    if fallback in mapping_macs.keys():
        toggle_switch(fallback)

def touch_temp_mqtt(client,userdata,message):

    fallback = ast.literal_eval(str(message.payload.decode("utf-8")))['FallbackTopic']
    #print(fallback,'--> TOGGLE')
    if fallback in mapping_macs.keys():
        toggle_temp(fallback)

def pir_mqtt(client,userdata,message):
    global mapping_macs
    fallback = ast.literal_eval(str(message.payload.decode("utf-8")))['FallbackTopic']
    presence_state = ast.literal_eval(str(message.payload.decode("utf-8")))['presence_state']
    if presence_state == 1:
        presence_state = True
    else:
        presence_state = False
    print(mapping_macs.keys())
    if fallback in mapping_macs.keys():
        print("entre y mande", mapping_macs[fallback])
        take_action_pir(fallback, presence_state,mapping_macs[fallback]['handles'],mapping_macs[fallback]["location"],mapping_macs[fallback]["str_id"])

########################################
#broker_address="192.168.2.20"
broker_address="127.0.0.1"
client = mqtt.Client("web_app") #create new instance
client.will_set("tele/sonoff/LWT", payload="gorda traga leche", qos=0, retain=True)
client.message_callback_add("tele/sonoff/INFO1", info1_mqtt)
client.message_callback_add("stat/sonoff/RESULT", result_mqtt)
client.message_callback_add("switch/NEW_SWITCH",add_switch_mqtt )
client.message_callback_add("temp/NEW_TEMP",add_temp_mqtt )
client.message_callback_add("temp/TOUCH",touch_temp_mqtt )
client.message_callback_add("switch/TOUCH",touch_switch_mqtt )
client.message_callback_add("switch/PIR",pir_mqtt )
client.on_message=callback_mqtt #attach function to callback
client.connect(host=broker_address,port=1883) #connect to broker
client.subscribe("+/sonoff/+",qos=2)
client.subscribe("switch/+",qos=2)
client.subscribe("temp/+",qos=2)



def server_mqtt():
    #print('starting mqtt server')

    client.loop_start() #start the loop


def start_server():
    host = "127.0.0.1"
    port = 8888  # arbitrary non-privileged port

    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    soc.setsockopt(
        socket.SOL_SOCKET, socket.SO_REUSEADDR, 1
    )  # SO_REUSEADDR flag tells the kernel to reuse a local socket in TIME_WAIT state, without waiting for its natural timeout to expire
    print("Socket created")

    try:
        soc.bind((host, port))
    except:
        print("Bind failed. Error : " + str(sys.exc_info()))
        sys.exit()

    soc.listen(1)  # queue up to 5 requests
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


def client_thread(connection, ip, port, max_buffer_size=5120):
    is_active = True

    while is_active:
        client_input = receive_input(connection, max_buffer_size)

        #print("Processed result: {}".format(client_input))
        connection.sendall("ok".encode("ascii", "ignore"))


def receive_input(connection, max_buffer_size):

    client_input = connection.recv(max_buffer_size)
    client_input_size = sys.getsizeof(client_input)

    if client_input_size > max_buffer_size:
        print("The input size is greater than expected {}".format(client_input_size))

    decoded_input = client_input.decode(
        "ascii", "ignore"
    )  # decode and strip end of line
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
    global low_baterry_not
    global Low_baterry_array
    global Current_state_dic_rooms
    global mail_batery_flag

    #print("Processing the input received from client")
    input_str = str(input_str).replace(chr(0), "")

    try:
        
        message = ast.literal_eval(input_str)
        #print(message)


        #print("pitu-->", message.keys(), message)
        if "sensor_update" in message.keys():
            #print('hasta aca va')
            mac_address = message["sensor_update"]["mac_address"]

            if message["sensor_update"]["battery"] == 1:
                battery = True
            else:
                battery = False

            if message["sensor_update"]["battery_state"] == 0:
                battery_state = True
            else:
                battery_state = False

            temp_state = message['sensor_update']['temp_state']

            if int(str(temp_state).split('.')[1])>5:
                temp_state= int(temp_state+1)
            else:
                temp_state = int(temp_state)
            #print('la temp state en el process input es de : ', temp_state)

            new = True
            for location in Current_sensors:
                if Current_sensors[location]["mac_address"] == mac_address:
                    new = False
                    Current_sensors[location]["battery"] = battery
                    Current_sensors[location]["battery_state"] = battery_state
                    Current_sensors[location]["temp_state"] = temp_state
                    Current_sensors[location]["online"] = True
                    Sensors_state[mac_address] = datetime.now()
                    #print('Current sensor', Sensors_state)

                    temp = get_temp_state()
                    #print('la temp promedio es: ',temp)
                    #print('temp in',temp,'location',location)
                    if temp != None:
                         
                        socketio.emit("update_temp",{"gtonoff": True,"general_temp": temp['Current_value'],'sensor_loc': location.replace(' ','_'),'sensor_temp': temp_state},namespace="/test")
                    else:
                        socketio.emit("update_temp",{"gtonoff": False,"general_temp": '-','sensor_loc': location.replace(' ','_'),'sensor_temp': temp_state},namespace="/test")
                         

                    if battery_state:
                        low_baterry_not = True

                        if mac_address not in mail_batery_flag.keys():

                            recipients_array = []
                            users= User.query.filter_by(admin=True)

                            for user in users:
                                recipients_array.append(user.user_email)
                            subject = 'Bateria Baja'
                            sender = 'no-reply@' + app.config['MAIL_SERVER']
                            recipients = recipients_array
                            text_body = 'El sensor en '+location+' tiene bateria baja'
                            html_body = '<h2> El sensor en '+location+ ' tiene bateria baja</h2>'
                            send_email(subject, sender, recipients, text_body, html_body)
                            mail_batery_flag[mac_address] = True

                        Low_baterry_array.append((location, mac_address))
                        socketio.emit("low_bat_tobrowser",{"arrayToSendToBrowser": Low_baterry_array},namespace="/test")
                        socketio.emit("low_bat_index",{"location": location.replace(' ','_'), "low_bat": True},namespace="/test")
                    else:
                        if mac_address in mail_batery_flag.keys():
                            mail_batery_flag.pop(mac_address)

                        socketio.emit("low_bat_index",{"location": location.replace(' ','_'), "low_bat": False},namespace="/test")

            #print('deberia llegar aca')
            if new and mac_address not in New_sensors.keys():
                #print('deberia llegar aca 2')
                New_sensors[mac_address] = {
                    "online": True,
                    "battery": battery,
                    "battery_state": battery_state,
                    "temp_state": temp_state,
                    "mac_address": mac_address,
                }
                flag = True
                new_dev_mac = list(New_devices.keys()) + list(New_sensors.keys())
                new_dev_mac_enabled = True
                #print('no entiendo')
                socketio.emit("new_dev_tobrowser",{"arrayToSendToBrowser": new_dev_mac},namespace="/test")
                #print('kii')
        return

    except Exception as e:
        #print(e)
        pass


def remove_sens(user, mac_address):
    global Current_sensors
    sensor_to_delete = Sensors.query.filter_by(mac_address=mac_address).first()

    sensor_location = sensor_to_delete.location
    db.session.delete(sensor_to_delete)

    description = "Sensor has been removed from " + sensor_location
    log_entry = Log(
        user=user,
        timestamp=datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        description=description,
    )
    db.session.add(log_entry)

    del Current_sensors[sensor_location]
    db.session.commit()
    scheduler.remove_job(mac_address)
    return "The sensor was successfully removed from " + sensor_location


def remove_dev(user, location_str_id):
    print(location_str_id)

    location = " ".join(location_str_id.split("/")[0].split("-"))
    str_id = " ".join(location_str_id.split("/")[1].split("."))

    global Current_state_dic_rooms
    global mapping_macs
    device_to_remove = Devices.query.filter_by(location=location, str_id=str_id).first()

    gettin_possible_switch = Devices.query.filter_by(location=location,tactil_switch=True)
    #print(gettin_possible_switch)

    if gettin_possible_switch !=None:

        for switches in gettin_possible_switch:
            handles = switches.handles
            handles = ast.literal_eval(handles)
            #print('handles del switch antes',handles, 'str_id del dev a eliminar', str_id)
            for idx, dev in enumerate(handles):
                if dev == str_id.replace(' ','_'):
                    handles.pop(idx)
                    #print('handles del switch desp',handles)
                    switches.handles = str(handles)
                    Current_state_dic_rooms[location][switches.str_id]['handles']=str(handles)
                    mapping_macs[switches.mac_address]['handles']=str(handles)
        
        db.session.commit()


    if location == 'Temperature':
        print("elimine el job temp")
        scheduler.remove_job(device_to_remove.mac_address)




    scheduled_events_to_del = Scheduled_events.query.filter_by(
        location=location, str_id=str_id
    )
    pids = []
    for pid in scheduled_events_to_del:
        pids.append(pid.pid)

    if len(pids) != 0:
        delete_scheduled_event(pids)
        db.session.delete(scheduled_events_to_del)

    description = "Device " + str_id + " has been removed from " + location
    log_entry = Log(
        user=user,
        timestamp=datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        description=description,
    )
    db.session.add(log_entry)

    db.session.delete(device_to_remove)
    del Current_state_dic_rooms[location][str_id]
    if len(Current_state_dic_rooms[location]) == 0:
        del Current_state_dic_rooms[location]
    db.session.commit()
    return "Device " + str_id + " was successfully removed from " + location

def enable_pir_server(mac_address):
    global mapping_macs
    global Current_state_dic_rooms
    location =  mapping_macs[mac_address]['location']
    str_id = mapping_macs[mac_address]['str_id']

    if Current_state_dic_rooms[location][str_id]['pir_enabled']:

        socketio.emit("pir_enable",{"mac_address" : mac_address.replace(':','_'),"state": False }, namespace="/test")
        Current_state_dic_rooms[location][str_id]['pir_enabled'] = False

    else:
        socketio.emit("pir_enable",{"mac_address" : mac_address.replace(':','_'),"state": True }, namespace="/test")
        Current_state_dic_rooms[location][str_id]['pir_enabled'] = True
    return


def tick():
    #socketio.emit("presence_state_tobrowser",{"presence_ToSendToBrowser": ["Patio", True]},namespace="/test")
    #socketio.emit("update_temp",{"gtonoff": False,"general_temp": '30','sensor_loc': 'Patio','sensor_temp': '30'},namespace="/test")
    # if len(new_dev_mac) != 0:

    # socketio.emit('new_dev_tobrowser', {'arrayToSendToBrowser' : new_dev_mac}, namespace='/test')
    #socketio.emit('low_bat_tobrowser', {'arrayToSendToBrowser' : Low_baterry_array}, namespace='/test')
    print("Tick! The time is: %s" % datetime.now())


scheduler = config_scheduler()
scheduler.add_job(tick, "interval", seconds=60, id="basic", replace_existing=True)
scheduler.add_job(start_server,"date",run_date=datetime.now(),id="basic_server",replace_existing=True)
scheduler.add_job(server_mqtt,"date",run_date=datetime.now(),id="basic_server_mqtt",replace_existing=True)

scheduler.start()


def get_activity_log():
    return Log.query.all()


def get_initial_values():

    global Current_state_dic_temp
    global Current_state_dic_rooms
    global mapping_macs
    query_devices = Devices.query.all()
    for location in query_devices:
        mapping_macs[location.mac_address]={'location': location.location,'str_id':location.str_id,'handles':location.handles}
        if location.location in Current_state_dic_rooms.keys():
            Current_state_dic_rooms[location.location][location.str_id] = {
                "dev_type": location.dev_type,
                "State": location.state,
                "set_point": location.set_point,
                "user_perm": location.user_perm,
                "mac_address": location.mac_address,
                "temp_dev": location.temp_device,
                "tactil_switch" : location.tactil_switch,
                "handles" : location.handles,
                "online": True,
                "presence_state": False,
                "pir_enabled" : True,
            }
        else:
            Current_state_dic_rooms[location.location] = {
                location.str_id: {
                    "dev_type": location.dev_type,
                    "State": location.state,
                    "set_point": location.set_point,
                    "user_perm": location.user_perm,
                    "mac_address": location.mac_address,
                    "temp_dev": location.temp_device,
                    "tactil_switch" : location.tactil_switch,
                    "handles" : location.handles,
                    "online": True,
                    "presence_state": False,
                    "pir_enabled" : True,
                }
            }
    print(Current_state_dic_rooms)
    # query_temp=Temperature.query.first()
    # Current_state_dic_temp={ 'State' : query_temp.state,'Set_Point' : query_temp.set_point, 'Current_value': 25} # Hay que ver como medimos el current value y lo agregamos

    query_sensors = Sensors.query.all()

    for sensor in query_sensors:
        mapping_macs[sensor.mac_address]={'location': sensor.location}
        Current_sensors[sensor.location] = {
            "online": True,
            "mac_address": sensor.mac_address,
            "battery": sensor.battery,
            "battery_state": True,
            "temp_state": 20,
            "active_average": sensor.active_temp_avegare,
        }
        Sensors_state[sensor.mac_address] = sensor.last_update

    # #print(Current_state_dic_rooms)
    ##print(Current_sensors)
    return


def set_temp2(state,set_point,user):
    global Current_state_dic_rooms

    try:
        state = ast.literal_eval(state)
    except Exception as e:
        pass
    

    if state:
        Current_state_dic_rooms['Temperature']['Temperature']['State'] = True
        Current_state_dic_rooms['Temperature']['Temperature']['Set_point'] = set_point
        query_temp = Devices.query.filter_by(temp_device=True).first()
        query_temp.set_point = set_point
        db.session.commit()
        controlling_temp()
        #print('aca prendi')
        return jsonify({"status": 200})
    else:
        Current_state_dic_rooms['Temperature']['Temperature']['State'] = False
        sent=client.publish("temp/"+Current_state_dic_rooms['Temperature']['Temperature']['mac_address']+"/",'00',qos=2)
        #print('aca apague')
        return jsonify({"status": 200})


def controlling_temp(**kwargs):
    global temp_hist
    global Current_state_dic_rooms
    temp=get_temp_state()

    try:
 
        if Current_state_dic_rooms['Temperature']['Temperature']['State']:

            if temp_hist['state'] == 'off':

                set_point = temp['Set_Point']

            elif temp_hist['state'] == "heat":

                set_point = temp['Set_Point'] + 1 

            else:
                set_point = temp['Set_Point'] -1 



            #print(temp)

            if temp['Current_value'] != '-':
                if temp['Current_value'] > set_point:
                    sent=client.publish("temp/"+Current_state_dic_rooms['Temperature']['Temperature']['mac_address']+"/",'10',qos=2)
                    temp_hist['state'] = 'ac'
                elif temp['Current_value'] < set_point:
                    sent=client.publish("temp/"+Current_state_dic_rooms['Temperature']['Temperature']['mac_address']+"/",'11',qos=2)
                    temp_hist['state'] = 'heat'
                else:
                    sent=client.publish("temp/"+Current_state_dic_rooms['Temperature']['Temperature']['mac_address']+"/",'00',qos=2)
                    temp_hist['state'] = 'off'
                return
            else:
                sent=client.publish("temp/"+Current_state_dic_rooms['Temperature']['Temperature']['mac_address']+"/",'00',qos=2)
                temp_hist['state'] = 'off'
                Current_state_dic_rooms['Temperature']['Temperature']['State'] = False

        else:
            return
    except Exception as e:
           pass  
        

def set_temp(
    state, set_point, user
):  # Aca no tengo en cuenta si hay mas de un sector en las temperaturas, si los hay en el futuro hay que tocar esto
    global Current_state_dic_rooms
    global Sent_messages

    query_temp = Devices.query.filter_by(temp_device=True).first()

    mac_address = query_temp.mac_address

    # seq_num=take_action(mac_address,state,set_point)
    ans,reset = take_action(mac_address, state, set_point,tactil_switch=False,handles='[]',location='Temperature',str_id='Temperature')

    if True:
        Current_state_dic_rooms["Temperature"]["Temperature"]["State"] = state
        query_temp.state = state

        if not Current_state_dic_rooms["Temperature"]["Temperature"]["dev_type"]:
            Current_state_dic_rooms["Temperature"]["Temperature"][
                "set_point"
            ] = set_point
            query_devices.set_point = set_point
        db.session.add(query_temp)
        db.session.commit()
        return jsonify({"status": 200})
    else:
        #print("la rompi devolviendo")
        return jsonify(
            {"status": 400, "str_id": "Temperature", "location": "Temperature"}
        )


def set_device(location, str_id, state, set_point):
    global Current_state_dic_rooms
    global Sent_messages

    query_devices = Devices.query.filter_by(location=location, str_id=str_id).first()

    mac_address = query_devices.mac_address
    handles = query_devices.handles
    tactil_switch = query_devices.tactil_switch


    ans,reset = take_action(mac_address, state, set_point,tactil_switch,handles,location,str_id)



    if True:
        return jsonify({"status": 200})
    else:
        #print("la rompi devolviendo")
        return jsonify({"status": 400, "str_id": str_id, "location": location})

def toggle_switch(mac_address):
    global mapping_macs
    global Current_state_dic_rooms
    take_action(mac_address, 'TOGGLE', 0,True,mapping_macs[mac_address]['handles'],mapping_macs[mac_address]['location'],mapping_macs[mac_address]['str_id'])
    return

def toggle_temp(mac_address):
    global Current_state_dic_rooms
    #print('aca va ',Current_state_dic_rooms['Temperature']['Temperature']['State'])

    socketio.emit("device_update",{"location": "","state": False if Current_state_dic_rooms['Temperature']['Temperature']['State'] else True ,"str_id":""}, namespace="/test")
    return

def get_temp_state():
    global Current_sensors
    global Current_state_dic_rooms
    temp_dev = Devices.query.filter_by(temp_device=True).first()
    if temp_dev != None:
        aux_temp = 0
        active = False
        count = 0

        for key in Current_sensors.keys():
            if (
                Current_sensors[key]["online"] == True
                and Current_sensors[key]["active_average"] == True
            ):  # --> hacemos un promedio de los sensores que esten activos y activos para el average
                active = True
                aux_temp += Current_sensors[key]["temp_state"]
                count += 1

        if active:
            tem_prom = float(aux_temp / count)
            if int(str(tem_prom).split('.')[1])>5:
                tem_prom= int(tem_prom+1)
            else:
                tem_prom = int(tem_prom)
        else:
            tem_prom = "-"

        return {
            "State": Current_state_dic_rooms["Temperature"]["Temperature"]['State'],
            "Set_Point": temp_dev.set_point,
            "Current_value": tem_prom,
            "online": Current_state_dic_rooms["Temperature"]["Temperature"]["online"],
        }
    else:
        return None

def get_switches():
    new_switches={}
    
    for mac,devs in New_devices.items():
        if devs['tactil_switch']:
            new_switches[mac]=devs

    if len(new_switches)!=0:
        return new_switches
    else:
        return None

def get_devices():
    ### esto se fija en cada room si hay al menos un sensor conectado y con presencia y si hay alguno online
    state = {}

    for key, value in Current_state_dic_rooms.items():
        
        presence_state = False
        online = False
        tactil_switch = False
        for k, v in value.items():
            #print(k,v)
            
            if v["tactil_switch"]:
                tactil_switch = True
                if v["presence_state"]:
                    presence_state = True
                if v["online"]:
                    online = True
        state[key] = {"presence_state": presence_state, "online": online, "tactil_switch": tactil_switch}

    return Current_state_dic_rooms, state  # --> que se la arrgle routes


def get_scheduled_events(*args):

    if args:
        query_scheduled = Scheduled_events.query.filter_by(
            str_id=args[0], location=args[1]
        ).all()
    else:
        query_scheduled = Scheduled_events.query.all()

    return query_scheduled


def alarm(state, set_point, event_type, id_job, mac_address, user,str_id,tactil_switch,handles,location):
    #print(event_type)
    if event_type == "date":
        #print("que onda")
        delete_scheduled_event(user, id_job)

        # aca falta llamar al cliente para que mande el mensaje al programa en C
    if state == True:
        state = 1
    else:
        state = 0
    #acá deberiamos llamar a take_action no? acho que sim
    ans=take_action(mac_address,state,set_point,tactil_switch,handles,location,str_id)
    if type(ans)==str:
        description = ans +" when trying to execute scheduled event for " + str_id 
        log_entry = Log(
            user=user,
            timestamp=datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            description=description,
        )
        db.session.add(log_entry)
        db.session.commit()
        
    '''
    message = " 1 " + mac_address + " " + str(state) + " " + str(set_point)
    message = str(len(message) + 1) + message
    send_socket(message)
    #print(state, set_point, event_type, id_job)
    '''

def schedule_event(
    user,
    str_id,
    location,
    start_date,
    pidd,
    param_state,
    param_set_point,
    args=[],
    day_of_week=[],
):
    str_id = str_id.replace("_", " ")
    location = location.replace('_',' ')
    try:
        if len(start_date.split(":")) == 3:
            start_date = start_date[:-3]
        date_date = start_date.replace("T", " ") + ":00"
    except:
        ans = {"status": 400, "pid": "", "error_message": "Date/hour needed"}

        return jsonify(ans)

    # #print(pidd)
    check_date = check_days(date_date, day_of_week, str_id, location, pidd)
    reschedule = False

    if pidd != "None" and check_date == False:
        event_to_reschedule = Scheduled_events.query.filter_by(pid=pidd).first()
        reschedule = True
        db.session.delete(event_to_reschedule)
        db.session.commit()

    if check_date == True:

        ans = {
            "status": 400,
            "pid": "",
            "error_message": "Try picking another day/hour for this device",
        }

        return jsonify(ans)

    else:

        if param_state == "On":
            param_state = True
        else:
            param_state = False
        dat = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        id_job = user + "_" + dat

        date = start_date.split("T")[0]
        try:
            hour = start_date.split("T")[1].split(":")[0]
            minute = start_date.split("T")[1].split(":")[1]
        except:
            ans = {"status": 400, "pid": "", "error_message": "Date/hour needed"}

            return jsonify(ans)

        getting_mac = Devices.query.filter_by(location=location, str_id=str_id).first()

        if len(day_of_week) != 0:

            scheduler.add_job(
                alarm,
                "date",
                run_date=date_date,
                args=[
                    param_state,
                    param_set_point,
                    "cron",
                    id_job,
                    getting_mac.mac_address,
                    user,
                    str_id,
                    getting_mac.tactil_switch,
                    getting_mac.handles,
                    location,
                ],
                id=id_job,
            )
            scheduler.add_job(
                alarm,
                "cron",
                start_date=date,
                day_of_week=",".join(day_of_week),
                hour=hour,
                minute=minute,
                args=[
                    param_state,
                    param_set_point,
                    "cron",
                    id_job,
                    getting_mac.mac_address,
                    user,
                    str_id,
                    getting_mac.tactil_switch,
                    getting_mac.handles,
                    location,
                ],
                id=id_job + "_cron",
            )  # para que lo haga ese dia y despues repita

            days = {
                "0": "Mon",
                "1": "Tue",
                "2": "Wed",
                "3": "Thu",
                "4": "Fri",
                "5": "Sat",
                "6": "Sun",
            }
            cron_days = []
            for day in day_of_week:
                cron_days.append(days[day])

            event_to_schedule = Scheduled_events(
                user=user,
                str_id=str_id,
                location=location,
                event_date=date_date,
                event_type="cron",
                event_cron=".".join(cron_days),
                event_param_state=param_state,
                event_param_setpoint=param_set_point,
                pid=id_job + "_cron",
            )

            hour_minute = hour + ":" + minute

            ans = {
                "status": 200,
                "pid": id_job + "_cron",
                "date": date_date,
                "hour": hour_minute,
                "type": "cron",
                "cron_days": cron_days,
                "location": location,
                "str_id": str_id,
                "reschedule": reschedule,
                "old_pid": pidd,
                "param_state": param_state,
                "param_set_point": param_set_point,
            }

        else:

            scheduler.add_job(
                alarm,
                "date",
                run_date=date_date,
                args=[
                    param_state,
                    param_set_point,
                    "date",
                    id_job,
                    getting_mac.mac_address,
                    user,
                    str_id,
                    getting_mac.tactil_switch,
                    getting_mac.handles,
                    location,
                ],
                id=id_job,
            )
            event_to_schedule = Scheduled_events(
                user=user,
                str_id=str_id,
                location=location,
                event_date=date_date,
                event_type="date",
                event_cron=None,
                event_param_state=param_state,
                event_param_setpoint=param_set_point,
                pid=id_job,
            )
            ans = {
                "status": 200,
                "pid": id_job,
                "date": date_date,
                "hour": hour,
                "type": "date",
                "cron_days": None,
                "location": location,
                "str_id": str_id,
                "reschedule": reschedule,
                "old_pid": pidd,
                "param_state": param_state,
                "param_set_point": param_set_point,
            }

        description = "An event for " + str_id + " in " + location + " has been set"
        log_entry = Log(
            user=user,
            timestamp=datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            description=description,
        )
        db.session.add(log_entry)
        db.session.add(event_to_schedule)
        db.session.commit()

        return jsonify(ans)


def check_days(date, day_of_week, str_id, location, pidd):

    # aca hay primero que ver si alguna tupla str_id y location coinciden, si no es asi, return false, sino ahi ver len(day_of_week)

    events = get_scheduled_events(
        str_id, location
    )  # --> Ojo que esto puede ser una lista
    flag = False
    if events == None:
        return False
    else:

        for scheduled_event in events:
            if (
                scheduled_event.event_type == "date"
                and len(day_of_week) == 0
                and scheduled_event.event_date == date
            ):  # len()==0 implica date y no cron(date)
                if pidd != scheduled_event.pid:
                    flag = True
                    break
            elif (
                scheduled_event.event_type == "cron"
                and len(day_of_week) != 0
                and scheduled_event.event_date.split(" ")[1] == date.split(" ")[1]
            ):  # si ambos son cron y la hora coincide, checkeo dias
                for day in scheduled_event.event_cron.split("."):
                    if day in day_of_week:
                        if pidd != scheduled_event.pid:
                            flag = True
                            break

            elif (
                scheduled_event.event_date.split(" ")[1] == date.split(" ")[1]
            ):  # solo entro en caso de que matcheen las horas

                if scheduled_event.event_type == "cron":
                    days = {
                        "Mon": "0",
                        "Tue": "1",
                        "Wed": "2",
                        "Thu": "3",
                        "Fri": "4",
                        "Sat": "5",
                        "Sun": "6",
                    }
                    aux = []
                    for day in scheduled_event.event_cron.split("."):
                        aux.append(days[day])
                    d = datetime.strptime(
                        scheduled_event.event_date.split(" ")[0], "%Y-%m-%d"
                    ).date()  # dia minimo a partir del cual el cron empieza a funcionar
                    weekday = list(
                        map(int, aux)
                    )  # paso la lista de strings a lista de ints
                    dia_que_quiero = datetime.strptime(
                        date.split(" ")[0], "%Y-%m-%d"
                    ).date()
                else:
                    # mismo que el anterior solo que se invierte el orden de dia que quiero y dia que tengo
                    d = datetime.strptime(
                        date.split(" ")[0], "%Y-%m-%d"
                    ).date()  # dia minimo a partir del cual el cron empieza a funcionar
                    weekday = list(
                        map(int, day_of_week)
                    )  # paso la lista de strings a lista de ints
                    dia_que_quiero = datetime.strptime(
                        scheduled_event.event_date.split(" ")[0], "%Y-%m-%d"
                    ).date()

                def next_weekday(d, weekday_list):

                    days = []
                    for weekday in weekday_list:
                        days_ahead = weekday - d.weekday()
                        if days_ahead <= 0:  # Target day already happened this week
                            days_ahead += 7
                        days.append(d + timedelta(days_ahead))
                    return days

                array_dates = next_weekday(d, weekday)

                # #print(array_dates)

                for datee in array_dates:
                    aux_date = datee
                    while aux_date <= dia_que_quiero:
                        if aux_date == dia_que_quiero:
                            if pidd != scheduled_event.pid:
                                # #print('hijo de mill',aux_date)
                                flag = True
                                break
                        else:
                            aux_date += timedelta(days=7)

    return flag


def delete_scheduled_event(user, id_event):

    if (
        type(id_event) == list
    ):  # Esto es por si elimino un usuario para eliminar todos los eventos que tenia schedulizados
        for pid in id_event:
            scheduler.remove_job(pid)
    else:
        aux = id_event.split("_")
        if "cron" in aux:
            aux.remove("cron")
            scheduler.remove_job(id_event)

            try:
                scheduler.remove_job("_".join(aux))
            except Exception as e:
                pass

        else:
            try:
                scheduler.remove_job(id_event)
            except Exception as e:
                pass
        event = Scheduled_events.query.filter_by(pid=id_event).first()

        description = (
            "An event for "
            + event.str_id
            + " in "
            + event.location
            + " has been deleted"
        )
        log_entry = Log(
            user=user,
            timestamp=datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            description=description,
        )
        db.session.add(log_entry)
        db.session.delete(event)
        db.session.commit()

    return


def get_new_device():

    # return {'flag': flag,'new_dev_mac':new_dev_mac,'new_dev_mac_enabled':new_dev_mac_enabled}
    return flag, new_dev_mac, new_dev_mac_enabled


def get_new_notifications():
    global Current_sensors
    global low_baterry_not
    global Low_baterry_array

    return {
        "flag": flag,
        "new_dev_mac": new_dev_mac,
        "new_dev_mac_enabled": new_dev_mac_enabled,
        "flag_bat": low_baterry_not,
        "sensors_list": Low_baterry_array,
    }


def disable_low_battery_notifications_server():
    global low_baterry_not
    global Low_baterry_array

    if low_baterry_not:
        Low_baterry_array = []

        low_baterry_not = False
    return


def edit_device_server(
    old_location, new_location, old_str_id, new_str_id, mac_address,handles
):
    global Current_rooms
    global Current_state_dic_rooms
    global mapping_macs

    old_location = old_location.replace('_',' ')
    old_str_id = old_str_id.replace('_',' ')
    new_str_id = new_str_id.replace('_',' ')
    new_location = new_location.replace('_',' ')

    #print(old_location,old_str_id,new_location,new_str_id)
    device_to_edit = Devices.query.filter_by(mac_address=mac_address).first()
    trying_to_change = Devices.query.filter_by(
        location=new_location, str_id=new_str_id
    ).first()

    if trying_to_change != None and trying_to_change.handles == handles:
        message = (
            "There's already a device called " + new_str_id + " in " + new_location
        )
        return {"status": 400, "message": message}
    else:


        device_to_edit.location = new_location
        device_to_edit.str_id = new_str_id
        device_to_edit.handles = str(handles)
        print('seteando el nuevo handles a ->',str(handles))
        Current_state_dic_rooms[old_location][old_str_id]['handles'] = str(handles)
        mapping_macs[mac_address]['location'] = new_location
        mapping_macs[mac_address]['str_id'] = new_str_id
        mapping_macs[mac_address]['handles']=str(handles)



        # device_to_add = Devices(user_perm=device_to_edit.user_perm,str_id=new_str_id,location=new_location,dev_type=device_to_edit.dev_type,state=state,set_point=set_point,new_device=False,mac_address=mac_address)
        if new_location not in Current_state_dic_rooms.keys():
            Current_state_dic_rooms[new_location] = {
                new_str_id: Current_state_dic_rooms[old_location][old_str_id]
            }
            # Current_rooms[new_location]=True
        else:
            #print('aca deberia entrar porque existe todo')
            Current_state_dic_rooms[new_location][new_str_id] =  Current_state_dic_rooms[old_location][old_str_id]


        if new_location != old_location or new_str_id != old_str_id:
            Current_state_dic_rooms[old_location].pop(old_str_id)
        if len(Current_state_dic_rooms[old_location]) == 0:
            Current_state_dic_rooms.pop(old_location)

        # db.session.delete(device_to_edit)
        db.session.commit()
        # db.session.add(device_to_add)device_to_add = Devices(user_perm=device_to_edit.user_perm,str_id=new_str_id,location=new_location,dev_type=device_to_edit.dev_type,state=state,set_point=set_point,new_device=False,mac_address=mac_address)
        # db.session.commit()

        return {
            "status": 200,
            "message": "Device "
            + new_str_id
            + " has been successfully added to "
            + new_location,
        }


def edit_sensor_server(old_location, new_location, mac_address, active_average):
    global Current_sensors


    old_location = old_location.replace('_',' ')
    new_location = new_location.replace('_',' ')

    if active_average == "True":
        active_average = True
    else:
        active_average = False

    if new_location == old_location:
        sensor_to_edit = Sensors.query.filter_by(mac_address=mac_address).first()

        sensor_to_edit.active_temp_avegare = active_average

        db.session.add(sensor_to_edit)

        Current_sensors[new_location]["active_average"] = active_average

        db.session.commit()
        return {
            "status": 200,
            "message": "Sensor in "
            + old_location
            + " is now being taken into account for temp calculation",
        }
    else:

        if new_location in Current_sensors.keys():
            message = "There's already a sensor in " + new_location
            return {"status": 400, "message": message}

        sensor_to_edit = Sensors.query.filter_by(mac_address=mac_address).first()

        sensor_to_edit.location = new_location
        sensor_to_edit.active_temp_avegare = active_average

        db.session.add(sensor_to_edit)

        Current_sensors[new_location] = Current_sensors[old_location]
        Current_sensors[new_location]["active_average"] = active_average
        del Current_sensors[old_location]

        db.session.commit()

        return {
            "status": 200,
            "message": "Sensor has been successfully moved from "
            + old_location
            + " to "
            + new_location,
        }


def add_new_device_server(
    user,
    location,
    str_id,
    state,
    set_point,
    mac_address,
    temp_dev,
    presence_state,
    online,
    tactil_switch,
    handles,
):
    global flag
    global new_dev_mac
    global Current_rooms
    global New_sensors
    global mapping_macs
    location = location.replace('_',' ').replace('-',' ')
    str_id = str_id.replace('_',' ').replace('-',' ')

    #print('should have made it to this point',location,str_id,handles)

    trying_to_add = Devices.query.filter_by(location=location, str_id=str_id).first()

    if trying_to_add != None:
        message = "There's already a device called " + str_id + " in " + location
        return {"status": 400, "message": message}
    else:
        if state == "On":
            state = True
        else:
            state = False

        temp_dev= ast.literal_eval(temp_dev)


        presence_state = ast.literal_eval(presence_state)
        online = ast.literal_eval(online)
        tactil_switch = ast.literal_eval(tactil_switch)
        handles=str(handles)

        print('cuando agrego el switch el handles es: ',handles)
        mapping_macs[mac_address]={'location': location,'str_id':str_id,'handles':handles}

        device_to_add = Devices(
            user_perm=True,
            str_id=str_id,
            location=location,
            dev_type=New_devices[mac_address]["dev_type"],
            state=state,
            set_point=int(set_point),
            temp_device=temp_dev,
            mac_address=mac_address,
            tactil_switch = tactil_switch,
            handles = str(handles),
        )

        if location not in Current_state_dic_rooms.keys():
            Current_state_dic_rooms[location] = {
                str_id: {
                    "dev_type": New_devices[mac_address]["dev_type"],
                    "State": state,
                    "set_point": int(set_point),
                    "user_perm": True,
                    "mac_address": mac_address,
                    "temp_dev": temp_dev,
                    "online": online,
                    "presence_state": presence_state,
                    "tactil_switch" : tactil_switch,
                    "handles" : str(handles),
                    "pir_enabled": True,
                }
            }
        # Current_rooms[location]=False
        else:
            if str_id not in Current_state_dic_rooms[location]:
                Current_state_dic_rooms[location][str_id] = {
                    "dev_type": New_devices[mac_address]["dev_type"],
                    "State": state,
                    "set_point": int(set_point),
                    "user_perm": True,
                    "mac_address": mac_address,
                    "temp_dev": temp_dev,
                    "online": online,
                    "presence_state": presence_state,
                    "tactil_switch": tactil_switch,
                    "handles":str(handles),
                    "pir_enabled": True,
                }
        description = "New device " + str_id + " has been added to " + location
        log_entry = Log(
            user=user,
            timestamp=datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            description=description,
        )
        db.session.add(log_entry)

        db.session.add(device_to_add)
        db.session.commit()
        New_devices.pop(mac_address)
        new_dev_mac = list(New_devices.keys()) + list(New_sensors.keys())
        if len(new_dev_mac) == 0:
            # #print('flag server entro bien ')
            flag = False
        return {
            "status": 200,
            "message": "Device "
            + str_id
            + " has been successfully added to "
            + location,
            "ndkl": len(new_dev_mac),
        }


def add_new_sensor_server(
    user,
    location,
    mac_address,
    battery,
    online,
    battery_state,
    temp_state,
    active_average,
):

    online = ast.literal_eval(online)
    battery = ast.literal_eval(battery)
    active_average = ast.literal_eval(active_average)
    battery_state = ast.literal_eval(battery_state)
    location = location.replace('_',' ').replace('-',' ')

    #print('la temp cuando agrego es : ',str(int(temp_state)))
    global flag
    global new_dev_mac
    global New_sensors
    global Current_sensors
    global low_baterry_not
    global Low_baterry_array
    global mapping_macs

    if location in Current_sensors.keys():
        return {
            "status": 400,
            "message": "There is already a sensor with that name in that room",
        }
    else:
        Current_sensors[location] = {
            "online": online,
            "mac_address": mac_address,
            "battery": battery,
            "battery_state": battery_state,
            "temp_state": int(temp_state),
            "active_average": active_average,
        }
    mapping_macs[mac_address]={'location':location}
    sensor_to_add = Sensors(
        location=location,
        battery=battery,
        mac_address=mac_address,
        active_temp_avegare=active_average,
    )
    description = "New sensor has been added to " + location
    log_entry = Log(
        user=user,
        timestamp=datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        description=description,
    )
    db.session.add(log_entry)
    db.session.add(sensor_to_add)
    db.session.commit()
    Sensors_state[mac_address] = datetime.now()
    scheduler.add_job(
        check_sensor_state, "interval", seconds=60, args=[mac_address], id=mac_address
    )
    New_sensors.pop(mac_address)

    if battery_state:
        low_baterry_not = True
        Low_baterry_array.append((location, mac_address))
        #print("pituuuu")
    new_dev_mac = list(New_devices.keys()) + list(New_sensors.keys())
    if len(new_dev_mac) == 0:
        # #print('flag server entro bien ')
        flag = False
    return {
        "status": 200,
        "message": "Sensor has been successfully added to " + location,
        "ndkl": len(new_dev_mac),
    }


def check_sensor_state(mac_address):
    global Current_sensors
    global Sensors_state
    global mail_sensor_flag
    global mapping_macs

    # #print('hola, estoy checkeando si el sensor '+mac_address+" está vivito y coleando")
    for sensor in Current_sensors:
        #print('sensor in check_sensor',sensor)
        if mac_address == Current_sensors[sensor]["mac_address"]:
            if (
                round((datetime.now() - Sensors_state[mac_address]).total_seconds() / 60 ) < 1 ):
                Current_sensors[sensor]["online"] = True
                if mac_address in mail_sensor_flag.keys():
                    mail_sensor_flag.pop(mac_address)
                #socketio.emit("sensor_online",{"sensor_loc": sensor,"sensor_state": True},namespace="/test")
            else:

                Current_sensors[sensor]["online"] = False
                if mac_address not in mail_sensor_flag.keys():
                    mail_sensor_flag[mac_address] = True
                    recipients_array = []
                    users= User.query.filter_by(admin=True)

                    for user in users:
                        recipients_array.append(user.user_email)
                    subject = 'Sensor Desconectado'
                    sender = 'no-reply@' + app.config['MAIL_SERVER']
                    recipients = recipients_array
                    text_body = 'El sensor en '+mapping_macs[mac_address]['location']+' se desconectó'
                    html_body = '<h2> El sensor en '+mapping_macs[mac_address]['location']+' se desconectó</h2>'
                    send_email(subject, sender, recipients, text_body, html_body)


                    socketio.emit("sensor_online",{"sensor_loc":sensor,"sensor_state": False},namespace="/test")

    return

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email, args=(app, msg)).start()

def get_new_devices():

    new_devices={}
    
    for mac,devs in New_devices.items():
        if not devs['tactil_switch']:
            new_devices[mac]=devs

    if len(new_devices)!=0:
        return new_devices
    else:
        return None


def get_temp_device():
    temp_device = Devices.query.filter_by(temp_device=True).first()
    return temp_device


def get_current_sensors():
    global Current_sensors
    return Current_sensors


def generate_dummy_device_test(dev_type, presence_state, online,switch,temp_dev):

    dev_type = ast.literal_eval(dev_type)
    presence_state = ast.literal_eval(presence_state)
    online = ast.literal_eval(online)
    switch = ast.literal_eval(switch)
    temp_dev = ast.literal_eval(temp_dev)
    ## Agrego un dispositivo al diccionario simplemente para probar el metodo 'Add device' simulando un nuevo dispositivo que se incorpora al sistema
    global flag
    global new_dev_mac
    global new_dev_mac_enabled
    global New_sensors

    if "08:00:27:60:03:90" not in New_devices.keys():
        New_devices["08:00:27:60:03:90"] = {
            "presence_state": presence_state,
            "dev_type": dev_type,
            "State": False,
            "set_point": None,
            "user_perm": False,
            "online": online,
            "new_device": True,
            "tactil_switch" : switch,
            "temp_dev" : temp_dev,
            "handles": '[]',
            "mac_address": "08:00:27:60:03:90",
        }
    else:

        New_devices["08:00:27:60:03:9" + str(len(New_devices.keys()))] = {
            "presence_state": presence_state,
            "dev_type": dev_type,
            "State": False,
            "set_point": None,
            "user_perm": False,
            "online": online,
            "new_device": True,
            "tactil_switch" : switch,
            "temp_dev" : temp_dev,
            "handles" : '[]',
            "mac_address": "08:00:27:60:03:9" + str(len(New_devices.keys())),
        }

    # #print(New_devices)

    flag = True
    new_dev_mac = list(New_devices.keys()) + list(New_sensors.keys())
    new_dev_mac_enabled = True

    # socketio.emit('new_dev_mac_enabled', {'arrayToSendToBrowser' : new_dev_mac}, namespace='/test')
    return


def generate_dummy_sensor_test(online, battery, battery_state, temp_state):

    online = ast.literal_eval(online)
    battery = ast.literal_eval(battery)
    battery_state = ast.literal_eval(battery_state)
    ## Agrego un dispositivo al diccionario simplemente para probar el metodo 'Add device' simulando un nuevo dispositivo que se incorpora al sistema
    global flag
    global new_dev_mac
    global new_dev_mac_enabled
    global New_devices
    global low_baterry_not

    if "08:00:27:60:04:00" not in New_sensors.keys():
        New_sensors["08:00:27:60:04:00"] = {
            "online": online,
            "battery": battery,
            "battery_state": battery_state,
            "temp_state": int(float(temp_state)),
            "mac_address": "08:00:27:60:04:00",
        }
    else:

        New_sensors["08:00:27:60:04:0" + str(len(New_sensors.keys()))] = {
            "online": online,
            "battery": battery,
            "battery_state": battery_state,
            "temp_state": int(float(temp_state)),
            "mac_address": "08:00:27:60:04:0" + str(len(New_sensors.keys())),
        }

    # #print(New_devices)
    flag = True
    new_dev_mac = list(New_devices.keys()) + list(New_sensors.keys())
    new_dev_mac_enabled = True
    return


def get_new_sensors():
    if len(New_sensors.keys()) != 0:
        return New_sensors
    else:
        return None


def disable_new_dev_mac():
    global new_dev_mac_enabled
    new_dev_mac_enabled = False
    return


def take_action(mac_address, state, set_point,tactil_switch,handles,location,str_id):
    global Sent_messages
    global Current_state_dic_rooms
    print(Current_state_dic_rooms)
    if state == True:
        state = 'ON'
    elif state == False:
        state = 'OFF'
    else:
        state = 'ON' if Current_state_dic_rooms[location][str_id]['State'] == False else 'OFF' 

   
    if tactil_switch:
        #print (handles)

        handles = ast.literal_eval(handles)

        reset = False
        aux_state=Current_state_dic_rooms[location][handles[0].replace('_',' ')]['State']
        #print(location,handles[0],aux_state,state)
        aux_mac_addresses=[]
        mac_loc_mapping = {}
        
        for dev in handles:
            ##print(dev,Current_state_dic_rooms[location][dev]['State'])
            if Current_state_dic_rooms[location][dev.replace('_',' ')]['State'] != aux_state:
                reset = True
            mac=Current_state_dic_rooms[location][dev.replace('_',' ')]['mac_address']
            aux_mac_addresses.append(mac)
            mac_loc_mapping[mac]={'location':location,'str_id':dev.replace('_',' ')}

        if reset:

            Current_state_dic_rooms[location][str_id]['State']= False if state=='ON' else True

        #print('reset',reset)
        for dev_mac in aux_mac_addresses:
            if reset:
                #client.publish("cmnd/"+dev_mac+"/POWER",'OFF',qos=2)
                #Current_state_dic_rooms[mac_loc_mapping[dev_mac]['location']][mac_loc_mapping[dev_mac]['str_id']]['State'] = False
                #socketio.emit("device_update",{"location": location.replace(' ','-'),"state": False ,"str_id":str_id.replace(' ','_')}, namespace="/test")
                socketio.emit("device_update",{"location": mac_loc_mapping[dev_mac]['location'].replace(' ','-'),"state": False,"str_id": mac_loc_mapping[dev_mac]['str_id'].replace(' ','_')}, namespace="/test")
                
            else:
                #client.publish("cmnd/"+dev_mac+"/POWER",'TOGGLE',qos=2)
                #Current_state_dic_rooms[mac_loc_mapping[dev_mac]['location']][mac_loc_mapping[dev_mac]['str_id']]['State'] = not Current_state_dic_rooms[mac_loc_mapping[dev_mac]['location']][mac_loc_mapping[dev_mac]['str_id']]['State']
                if aux_state and state == 'ON':
                    #socketio.emit("device_update",{"location": location.replace(' ','-'),"state": False ,"str_id":str_id.replace(' ','_')}, namespace="/test")
                    Current_state_dic_rooms[location][str_id]['State']= True
                if not aux_state and state == 'OFF':
                    #socketio.emit("device_update",{"location": location.replace(' ','-'),"state": True ,"str_id":str_id.replace(' ','_')}, namespace="/test")
                    Current_state_dic_rooms[location][str_id]['State']= False
                socketio.emit("device_update",{"location": mac_loc_mapping[dev_mac]['location'].replace(' ','-'),"state": not aux_state ,"str_id": mac_loc_mapping[dev_mac]['str_id'].replace(' ','_')}, namespace="/test")
        
       # if reset:
        #    socketio.emit("device_update",{"location": location.replace(' ','-'),"state": False ,"str_id":str_id.replace(' ','_')}, namespace="/test")
        #    Current_state_dic_rooms[location][str_id]['State']= False
        seq_number = random.randint(0, 256)
        return seq_number,reset
    else:

        ##print("single",mac_address,state,location,str_id)
        ##print('++++++++++++++++++++++++++++++')
        sent=client.publish("cmnd/"+mac_address+"/POWER",state,qos=2)
        socketio.emit("device_update",{"location": location.replace(' ','-'),"state": True if state=='ON' else False ,"str_id": str_id.replace(' ','_')}, namespace="/test")
        ##print(Current_state_dic_rooms[location][str_id]['State'])
        Current_state_dic_rooms[location][str_id]['State']= True if state=='ON' else False
        ##print(Current_state_dic_rooms[location][str_id]['State'])
        ##print(sent.is_published())
        seq_number = random.randint(0, 256)
        return seq_number,False

def take_action_pir(mac_address, state,handles,location,str_id):

    global Current_state_dic_rooms
    global mapping_macs

    socketio.emit("update_presence",{"location": location.replace(' ','_'),"presence_state": state }, namespace="/test")


    print(Current_state_dic_rooms[location][str_id]['pir_enabled'])
    if Current_state_dic_rooms[location][str_id]['pir_enabled']:

        print(handles)
        handles = ast.literal_eval(handles)

        for dev in handles:
            print(location,str_id)
            socketio.emit("device_update",{"location": location.replace(' ','-'),"state": state ,"str_id": dev.replace(' ','_')}, namespace="/test")
            Current_state_dic_rooms[location][dev.replace('_',' ')]['State'] = state

