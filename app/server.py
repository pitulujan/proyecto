from datetime import datetime
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
    
    return Current_state_dic['Lights'] #--> que se la arrgle routes
def get_set_point_light():
    
    return Current_state_dic['Light']

def get_current_temp():
    return 20

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

