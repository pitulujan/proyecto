from app import db
from app.models import User,Devices, Log , Temperature

temp = Temperature()

pitu = User(username='Pitu',admin=True)
pitu.set_password('pitu')
gordo =User(username='gordo',admin=False)
gordo.set_password('gordo')
db.session.add(pitu)
db.session.add(gordo)
db.session.add(temp)


device1 = Devices(user_perm=False,str_id='Luz Puerta',location='Cocina',dev_type=True,state=True,set_point=None)
device2 = Devices(user_perm=False,str_id='Luz Mesada',location='Cocina',dev_type=False,state=True,set_point=50)
device4 = Devices(user_perm=False,str_id='Luz Parrilla',location='Patio',dev_type=False,state=True,set_point=50)
device3 = Devices(user_perm=True,str_id='Riego',location='Patio',dev_type=True,state=False,set_point=None)
device5 = Devices(user_perm=False,str_id='Luz Ventana',location='Terraza',dev_type=True,state=True,set_point=None)
device6 = Devices(user_perm=False,str_id='Luz Reja',location='Terraza',dev_type=False,state=True,set_point=50)
db.session.add(device1)
db.session.add(device6)
db.session.add(device5)
db.session.add(device2)
db.session.add(device3)
db.session.add(device4)
db.session.commit()


event_test_uno= Scheduled_events(user='Pitu',str_id='Luz Mesada',location='Cocina',event_date='2019-2-10 09:30:00',event_date='cron',event_cron='mon.wen.fri', pid='tuvieja')
event_test_dos= Scheduled_events(user='Pitu',str_id='Luz Puerta',location='Cocina',event_date='2019-2-10 09:30:00',event_date='cron',event_cron='tue.thu', pid='tuviejapuerta')
event_test_tres= Scheduled_events(user='Pitu',str_id='Luz Mesada',location='Cocina',event_date='2019-2-15 09:30:00',event_date='date',event_cron=None,pid='tuviejamesada')








