from datetime import timedelta, datetime, date
from app.configuracion_scheduler import config_scheduler
from app.models import User, Devices, Log, Temperature, Scheduled_events
from app import db
from flask import jsonify
from app.socket_server import *


Current_state_dic_temp= {}
Current_state_dic_rooms ={}
New_devices={}
flag= False

start_server()          
 
                    
def add_device(user_perm,str_id,location,dev_type,state,set_point): #user_perm es true si el usuario es admin (ergo pasarle el valor desde routes)

    if location not in Current_state_dic_rooms.keys():
        Current_state_dic_rooms[location] = {str_id:{'dev_type' : dev_type, 'State': state , 'set_point' : set_point, 'user_perm' : user_perm}}
        new_device=Devices(user_perm=user_perm,str_id=str_id, location=location,dev_type=dev_type,state=state,set_point=set_point)
    else:
        if str_id not in Current_state_dic_rooms[location]:
            Current_state_dic_rooms[location][str_id] = {'dev_type' : dev_type, 'State': state , 'set_point' : set_point, 'user_perm' : user_perm}
            new_device=Devices(user_perm=user_perm,str_id=str_id, location=location,dev_type=dev_type,state=state,set_point=set_point)
        else:
            return 'Device "'+str_id+'" already exists, please try a different name'
    db.session.add(new_device)
    db.commit()
    return 'Device "'+str_id+'" added successfully' 

def remove_dev(location_str_id):

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
    
    db.session.delete(device_to_remove)
    del Current_state_dic_rooms[location][str_id]
    if len(Current_state_dic_rooms[location]) == 0:
        del Current_state_dic_rooms[location]
    db.session.commit()
    return 'Device '+str_id+' was successfully removed from '+location
                    

def tick():
    print('Tick! The time is: %s' % datetime.now())
scheduler = config_scheduler()
#scheduler.add_job(tick, 'interval', seconds=20,id='basic',replace_existing=True)
scheduler.start()

def get_initial_values():

    global Current_state_dic_temp
    global Current_state_dic_rooms
    query_devices=Devices.query.all()
    for location in query_devices:
        if location.location in Current_state_dic_rooms.keys():
            Current_state_dic_rooms[location.location][location.str_id]={'dev_type' : location.dev_type, 'State': location.state , 'set_point' : location.set_point, 'user_perm' : location.user_perm, 'new_device': location.new_device, 'offline':location.offline,'mac_address':location.mac_address}
        else:
            Current_state_dic_rooms[location.location] = {location.str_id:{'dev_type' : location.dev_type, 'State': location.state , 'set_point' : location.set_point, 'user_perm' : location.user_perm,'new_device': location.new_device, 'offline':location.offline,'mac_address':location.mac_address}}

    query_temp=Temperature.query.first()
    Current_state_dic_temp={ 'State' : query_temp.state,'Set_Point' : query_temp.set_point, 'Current_value': 25} # Hay que ver como medimos el current value y lo agregamos


    ##print(Current_state_dic_rooms)
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

def get_scheduled_events(*args):

    if args:
        query_scheduled = Scheduled_events.query.filter_by(str_id=args[0],location=args[1]).all()
    else:
        query_scheduled = Scheduled_events.query.all()
    
    return query_scheduled

def alarm(pitu,japon):
    print(pitu,japon)

def schedule_event(user,str_id,location,start_date,pidd,param_state,param_set_point,args=[], day_of_week=[]):
    str_id=str_id.replace('_',' ')

    if len(start_date.split(':'))==3:
        start_date=start_date[:-3]
    date_date=start_date.replace('T',' ')+':00'
    #print(pidd)
    check_date=check_days(date_date,day_of_week,str_id,location,pidd)
    reschedule=False

    if pidd != 'None' and check_date == False:
        event_to_reschedule = Scheduled_events.query.filter_by(pid=pidd).first()
        reschedule = True
        db.session.delete(event_to_reschedule)
        db.session.commit()


    if check_date == True:

        ans={'status':400,'pid':''}

        return jsonify(ans)

    else:

        if param_state == 'On':
            param_state=True
        else:
            param_state=False
        dat=datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        id_job=user+'_'+dat

        date=start_date.split('T')[0]

        hour= start_date.split('T')[1].split(':')[0]
        minute= start_date.split('T')[1].split(':')[1]

        if len(day_of_week)!=0:

            scheduler.add_job(alarm, 'date', run_date=date_date, args=[param_state,param_set_point],id=id_job)
            scheduler.add_job(alarm, 'cron', start_date=date, day_of_week=','.join(day_of_week), hour=hour, minute=minute , args=[param_state,param_set_point],id=id_job+'_cron') #para que lo haga ese dia y despues repita
            
            days={'0':'Mon','1':'Tue','2':'Wed','3':'Thu','4':'Fri','5':'Sat','6':'Sun'}
            cron_days=[]   
            for day in day_of_week:
                cron_days.append(days[day])

            event_to_schedule= Scheduled_events(user=user,str_id=str_id,location=location,event_date=date_date,event_type='cron',event_cron='.'.join(cron_days),event_param_state=param_state,event_param_setpoint=param_set_point, pid=id_job+'_cron')
            
            hour_minute = hour+':'+minute

            ans={'status':200,'pid':id_job+'_cron','date':date_date,'hour':hour_minute,'type':'cron','cron_days':cron_days,'location':location,'str_id':str_id,'reschedule': reschedule,'old_pid':pidd,'param_state':param_state,'param_set_point':param_set_point}
            

        else:

            scheduler.add_job(alarm, 'date', run_date=date_date, args=[param_state,param_set_point],id=id_job)
            event_to_schedule= Scheduled_events(user=user,str_id=str_id,location=location,event_date=date_date,event_type='date',event_cron=None,event_param_state=param_state,event_param_setpoint=param_set_point, pid=id_job)
            ans={'status':200,'pid':id_job,'date':date_date,'hour':hour,'type':'date','cron_days':None,'location':location,'str_id':str_id,'reschedule':reschedule,'old_pid':pidd,'param_state':param_state,'param_set_point':param_set_point}



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

def reschedule_event():
    pass

def delete_scheduled_event(id_event):

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
            scheduler.remove_job(id_event)
        event = Scheduled_events.query.filter_by(pid=id_event).first()
        db.session.delete(event)
        db.session.commit()

    return

def get_new_device():
    return flag

def edit_device_server(old_location,new_location,old_str_id,new_str_id,state,set_point,mac_address):

    device_to_edit = Devices.query.filter_by(mac_address=mac_address).first()
    trying_to_change = Devices.query.filter_by(location=new_location,str_id=new_str_id).first()

    if trying_to_change != None:
        return {'status': 400, 'message' : "There's already a device with that name in that location"}
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

def add_new_device_server(location,str_id,state,set_point,mac_address):
    global flag
    
    trying_to_add = Devices.query.filter_by(location=location,str_id=str_id).first()

    if trying_to_add != None:
        return {'status': 400, 'message' : "There's already a device with that name in that location"}
    else:
        if state == 'On':
            state = True
        else:
            state = False

        device_to_add = Devices(user_perm=New_devices[mac_address]['user_perm'],str_id=str_id,location=location,dev_type=New_devices[mac_address]['dev_type'],state=state,set_point=set_point,new_device=False,mac_address=mac_address)
        

        if location not in Current_state_dic_rooms.keys():
            Current_state_dic_rooms[location] = {str_id:{'dev_type' : New_devices[mac_address]['dev_type'], 'State': state , 'set_point' : set_point, 'user_perm' : New_devices[mac_address]['user_perm'],'mac_address': mac_address}}
        else:
            if str_id not in Current_state_dic_rooms[location]:
                Current_state_dic_rooms[location][str_id] = {'dev_type' : New_devices[mac_address]['dev_type'], 'State': state , 'set_point' : set_point, 'user_perm' : New_devices[mac_address]['user_perm'], 'mac_address': mac_address}

        db.session.add(device_to_add)
        db.session.commit()
        New_devices.pop(mac_address)
        if len(New_devices.keys())==0:  
            #print('flag server entro bien ')
            flag = False
        return {'status': 200, 'message' : "Device "+str_id+" has been successfully added to "+location , 'ndkl':len(New_devices.keys())}

def get_new_devices():

    if len(New_devices.keys())!=0:
        return New_devices
    else:
        return None

def generate_dummy_device_test(dev_type):
    if dev_type == 'True':
        dev_type = True
    else:
        dev_type = False 
    ## Agrego un dispositivo al diccionario simplemente para probar el metodo 'Add device' simulando un nuevo dispositivo que se incorpora al sistema
    global flag
    
    if '08:00:27:60:03:90' not in New_devices.keys():
        New_devices['08:00:27:60:03:90'] = {'dev_type' : dev_type , 'State': False , 'set_point' : None, 'user_perm' : False , 'new_device': True, 'offline': False, 'mac_address':'08:00:27:60:03:90'}
    else:
        
        New_devices['08:00:27:60:03:9'+str(len(New_devices.keys()))] = {'dev_type' : dev_type , 'State': False , 'set_point' : None, 'user_perm' : False , 'new_device': True, 'offline': False,'mac_address':'08:00:27:60:03:9'+str(len(New_devices.keys()))} 

    #print(New_devices)
    flag = True 
    return



            


