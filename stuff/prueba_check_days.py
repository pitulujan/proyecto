from datetime import timedelta, datetime
from app.configuracion_scheduler import config_scheduler
from app.models import User, Devices, Log, Temperature, Scheduled_events
from app import db
from flask import jsonify


#event_test_uno= Scheduled_events(user='Pitu',str_id='Luz Mesada',location='Cocina',event_date='2019-2-10 09:30:00',event_type='cron',event_cron='0.2.4', pid='tuvieja')

def get_scheduled_events(*args):

    if args:
        query_scheduled = Scheduled_events.query.filter_by(str_id=args[0],location=args[1]).all()
    else:
        query_scheduled = Scheduled_events.query.all()
    
    return query_scheduled

def check_days(date,day_of_week,str_id,location):

    #aca hay primero que ver si alguna tupla str_id y location coinciden, si no es asi, return false, sino ahi ver len(day_of_week)

    events = get_scheduled_events(str_id,location)  #--> Ojo que esto puede ser una lista 
    flag = False
    if events == None:
        return False   
    else:
        
        for scheduled_event in events: 
            if scheduled_event.event_type == 'date' and len(day_of_week)==0 and scheduled_event.event_date == date: #len()==0 implica date y no cron(date)
                flag=True 
                break 
            elif scheduled_event.event_type == 'cron' and len(day_of_week)!=0 and scheduled_event.event_date.split(' ')[1] == date.split(' ')[1]: #si ambos son cron y la hora coincide, checkeo dias
                for day in scheduled_event.event_cron.split('.'):
                    if day in day_of_week:
                        flag=True
                        break


            elif scheduled_event.event_date.split(' ')[1] == date.split(' ')[1]: #solo entro en caso de que matcheen las horas


                if scheduled_event.event_type == 'cron':
                    print('bien')
                    d=datetime.strptime(scheduled_event.event_date.split(' ')[0],'%Y-%m-%d').date() #dia minimo a partir del cual el cron empieza a funcionar
                    print('d',d)
                    weekday=list(map(int,scheduled_event.event_cron.split('.'))) #paso la lista de strings a lista de ints
                    print('weekday',weekday)
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

                print(array_dates)

                for datee in array_dates:
                    aux_date=datee
                    while aux_date <=dia_que_quiero:
                        if aux_date == dia_que_quiero:
                            print('hijo de mill',aux_date)
                            flag = True
                            break
                        else:
                            aux_date+=timedelta(days=7)

    return flag

if __name__ == '__main__':
	date='2019-2-10 09:31:00'
	day_of_week=['0','2','4']
	str_id='Luz Mesada'
	location='Cocina'
	pitu = check_days(date,day_of_week,str_id,location)

	if pitu:
		print ('no se puede schedualizar')
	else:
		print('se puede schedualizar')