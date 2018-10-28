from app.models import User, User_Light_State,User_Temperature_State,Scheduled_events
from app.server import delete_scheduled_event
from app import db

def create_user_full(form):

    create_user = User(username=form.username.data, admin=form.admin.data)
    create_user.set_password(form.password.data)
    create_light_state=User_Light_State(user=form.username.data)
    create_temp_state=User_Temperature_State(user=form.username.data)

    db.session.add(create_user)
    db.session.add(create_temp_state)
    db.session.add(create_light_state)
    db.session.commit()    
        
    return 'Congratulations, you have just registered '+form.username.data+'!'
    
def delete_user_full(user):

    delete_user = User.query.filter_by(username=user).first()
    light_state_to_del= User_Light_State.query.filter_by(user=user).first()   
    temp_state_to_del= User_Temperature_State.query.filter_by(user=user).first()  
    shceduled_events_to_del=Scheduled_events.query.filter_by(user=user)
    
    #Agarro tods los pids del usuario que voy a eliminar y se los mando al metodo para que la libreria apscheduler se haga cargo
    
    pids=[]
    for pid in shceduled_events_to_del:
        pids.append(pid.pid)
    
    if len(pids)!=0:
        delete_scheduled_event(pids)
        db.session.delete(shceduled_events_to_del)

    db.session.delete(delete_user)
    db.session.delete(light_state_to_del)
    db.session.delete(temp_state_to_del)
    
    db.session.commit()

    return 'Congratulations, you have just deleted '+delete_user.username+ ' from the users list!'