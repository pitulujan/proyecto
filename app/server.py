from datetime import datetime
import sqlite3
from app.configuracion_scheduler import config_scheduler
from app.models import User, Devices
from app import db




#route = '/home/pitu/proyecto/app.db'

'''
user_perm
    str_id
    location
    dev_type
    state
    set_point
'''

Current_state_dic_temp= {'Temperature':        { 'State' : False,'Set_Point' : 12, 'Current_value': 25}}
Current_state_dic_rooms ={'Cocina': {'Luz Puerta' : {'dev_type' : True, 'State': True , 'set_point' : None, 'user_perm' : False},
                                    'Luz Mesada': {'dev_type' : False, 'State': True , 'set_point' : 50, 'user_perm': False}},

                          'Patio' : {'Luz Parrilla' :{'dev_type' : False, 'State': True , 'set_point' : 50, 'user_perm': False},
                                     'Riego' :{'dev_type' : True, 'State': False , 'set_point' : None, 'user_perm': True}},                                    
                                    }
                        
 
                    
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



    query_devices=Devices.query.all()

    #for location in query_devices:

    query_lights=Current_Light_State.query.all()
    for place in query_lights:
        Current_state_dic['Lights'][place.location]['State']=place.light_state
        if place.dimmer == True:
            Current_state_dic['Lights'][place.location]['Intensity']=place.light_intensity
        


    query_temp=Current_Temperature_State.query.first() #Si hay mas temperaturas (mas sectores) cambiar el first por un all y sus respectivos cambios despues 
    Current_state_dic['Temperature']['State']=query_temp.temp_state
    Current_state_dic['Temperature']['Set_Point']=query_temp.temp_set_point

    query_bools= Current_Boolean_States.query.all()
    for boolean in query_bools:
        Current_state_dic['Booleans'][boolean.str_id]['State']= boolean.bool_state 

    print(Current_state_dic)
    return

def set_temp(state,setpoint,user):#Aca no tengo en cuenta si hay mas de un sector en las temperaturas, si los hay en el futuro hay que tocar esto
    
    query_temp=Current_Temperature_State.query.first()

    query_temp.temp_state = state
    Current_state_dic['Temperature']['State']=state
    if state==True:
        query_temp.temp_set_point = setpoint
        Current_state_dic['Temperature']['Set_Point']=setpoint
    query_temp.user = user
    query_temp.timestamp = datetime.now()

    db.session.add(query_temp)
    db.session.commit()



def set_light(state,setpoint,user,str_id):
    
    query_lights=Current_Light_State.query.filter_by(str_id=str_id).first()
    
    query_lights.user=user
    query_lights.light_state=state
    query_lights.light_intensity=setpoint
    
    Current_state_dic['Lights'][str_id]['State']=state
    Current_state_dic['Lights'][str_id]['Intensity']=setpoint
    
    db.session.add(query_lights)
    db.session.commit()


    return


def get_temp_state():
    return Current_state_dic['Temperature'] #Esto devuelve todo, el state, el set point y la current temp

def get_light_state():
    return Current_state_dic['Lights'] #--> que se la arrgle routes


def schedule_event(user,function,atribute,type=None,run_date=None,args=[],start_date=None,end_date=None,interval=None):



    scheduler.add_job(alarm, 'date', run_date='2018-10-21 20:42:00', args=[datetime.now()],id='Pitu 5')

    scheduler.add_job(alarm, 'interval', seconds=5, start_date='2018-10-10 09:30:00', end_date='2019-06-15 11:00:00',args=[datetime.now()],id='Pitu1')




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

