from app import db
from app.models import User,User_Temperature_State,Current_Light_State
from app.models import User_Light_State
from app.models import Current_Temperature_State

create_light_state=User_Light_State(user='Pitu',str_id='Cocina')
create_light_state2=User_Light_State(user='Pitu',str_id='Patio')
create_light_state3=User_Light_State(user='Pitu',str_id='Living')
db.session.add(create_light_state)
db.session.add(create_light_state2)
db.session.add(create_light_state3)
db.session.commit()


create_light_state=User_Light_State(user='gordo',str_id='Cocina')
create_light_state2=User_Light_State(user='gordo',str_id='Patio')
create_light_state3=User_Light_State(user='gordo',str_id='Living')
db.session.add(create_light_state)
db.session.add(create_light_state2)
db.session.add(create_light_state3)
db.session.commit()

create_temp_state=User_Temperature_State(user='Pitu')
db.session.add(create_temp_state)
db.session.commit()

create_temp_state=User_Temperature_State(user='gordo')
db.session.add(create_temp_state)
db.session.commit()


create_current_light= Current_Light_State(user='Pitu',str_id='Cocina')
create_current_light2= Current_Light_State(user='gordo',str_id='Patio')
create_current_light3= Current_Light_State(user='Pitu',str_id='Living')
db.session.add(create_current_light)
db.session.add(create_current_light2)
db.session.add(create_current_light3)
db.session.commit()


create_current_temp = Current_Temperature_State(user='Pitu')
db.session.add(create_current_temp)
db.session.commit()

