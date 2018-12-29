from datetime import datetime
import sqlite3
from app.configuracion_scheduler import config_scheduler
from app.models import User, Devices, Log, Temperature, Scheduled_events
from app import db


Current_state_dic_temp= {}
Current_state_dic_rooms ={}
                        
 
                    
def add_device(user_perm,str_id,location,dev_type,state,set_point):

    if location not in Current_state_dic_rooms.keys():
        Current_state_dic_rooms[location] = {str_id:{'dev_type' : dev_type, 'State': state , 'set_point' : set_point, 'user_perm' : user_perm}}
    else:
        if str_id not in Current_state_dic_rooms[location]:
            Current_state_dic_rooms[location][str_id] = {'dev_type' : dev_type, 'State': state , 'set_point' : set_point, 'user_perm' : user_perm}
            new_device=Devices()
        else:
            return 'Device "'+str_id+'" already exists, please try a different name'
    return 'Device "'+str_id+'" added successfully' 


                    

def tick():
    print('Tick! The time is: %s' % datetime.now())
scheduler = config_scheduler()
scheduler.add_job(tick, 'interval', seconds=20,id='basic',replace_existing=True)
#scheduler.start()

def get_initial_values():

    global Current_state_dic_temp
    global Current_state_dic_rooms
    query_devices=Devices.query.all()
    for location in query_devices:
        if location.location in Current_state_dic_rooms.keys():
            Current_state_dic_rooms[location.location][location.str_id]={'dev_type' : location.dev_type, 'State': location.state , 'set_point' : location.set_point, 'user_perm' : location.user_perm}
        else:
            Current_state_dic_rooms[location.location] = {location.str_id:{'dev_type' : location.dev_type, 'State': location.state , 'set_point' : location.set_point, 'user_perm' : location.user_perm}}

    query_temp=Temperature.query.first()
    Current_state_dic_temp={ 'State' : query_temp.state,'Set_Point' : query_temp.set_point, 'Current_value': 25} # Hay que ver como medimos el current value y lo agregamos


    print(Current_state_dic_rooms)
    return

def set_temp(state,setpoint,user):#Aca no tengo en cuenta si hay mas de un sector en las temperaturas, si los hay en el futuro hay que tocar esto
    global Current_state_dic_temp
    query_temp=Temperature.query.first()

    query_temp.state = state
    Current_state_dic_temp['State']=state
    if state==True:
        query_temp.set_point = setpoint
        Current_state_dic_temp['Set_Point']=setpoint

    db.session.add(query_temp)
    db.session.commit()

def set_device(location, str_id,state,set_point):
    global Current_state_dic_rooms
    
    query_devices=Devices.query.filter_by(location=location,str_id=str_id).first()

    Current_state_dic_rooms[location][str_id]['State'] = state
    query_devices.state=state

    if not Current_state_dic_rooms[location][str_id]['dev_type']:
        Current_state_dic_rooms[location][str_id]['set_point'] = set_point
        query_devices.set_point =set_point
    
    db.session.add(query_devices)
    db.session.commit()

        

def get_temp_state():
    return Current_state_dic_temp #Esto devuelve todo, el state, el set point y la current temp

def get_devices():
    return Current_state_dic_rooms #--> que se la arrgle routes

def get_scheduled_events():
    query_scheduled = Scheduled_events.query.all()
    #query_scheduled = User.query.all()
    return query_scheduled


def schedule_event(user,function,atribute,type=None,run_date=None,args=[],start_date=None,end_date=None,interval=None):



    scheduler.add_job(alarm, 'date', run_date='2018-10-21 20:42:00', args=[datetime.now()],id='Pitu 5')

    scheduler.add_job(alarm, 'interval', seconds=5, start_date='2018-10-10 09:30:00', end_date='2019-06-15 11:00:00',args=[datetime.now()],id='Pitu1')

    #datetime.now().strftime("%Y-%m-%d %H:%M")




    return

def reschedule_event():
    pass

def delete_scheduled_event(id_event):

    if type(id_event)==list: #Esto es por si elimino un usuario para eliminar todos los eventos que tenia schedulizados
        for pid in id_event:
            scheduler.remove_job(pid)
    else:
        scheduler.remove_job(id_event)

    return

