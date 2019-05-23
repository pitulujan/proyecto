from app.models import User, Scheduled_events,Log
from app.server import delete_scheduled_event
from app import db
from datetime import datetime

def create_user_full(form,user):

    create_user = User(username=form.username.data, admin=form.admin.data)
    create_user.set_password(form.password.data)

    description= "User "+form.username.data+" has been added."
    log_entry = Log(user=user,timestamp=datetime.now().strftime("%d/%m/%Y %H:%M:%S"),description = description)
    db.session.add(log_entry)


    db.session.add(create_user)

    db.session.commit()    
        
    return 'Congratulations, you have just registered '+form.username.data+'!'
    
def delete_user_full(user,current_user):

    delete_user = User.query.filter_by(username=user).first()
      
    shceduled_events_to_del=Scheduled_events.query.filter_by(user=user)
    
    #Agarro tods los pids del usuario que voy a eliminar y se los mando al metodo para que la libreria apscheduler se haga cargo
    
    pids=[]
    for pid in shceduled_events_to_del:
        pids.append(pid.pid)
    
    if len(pids)!=0:
        delete_scheduled_event(pids)
        db.session.delete(shceduled_events_to_del)

    description= "User "+user+" has been deleted."
    log_entry = Log(user=current_user,timestamp=datetime.now().strftime("%d/%m/%Y %H:%M:%S"),description = description)
    db.session.add(log_entry)    
    db.session.delete(delete_user)
    
    db.session.commit()

    return 'User '+delete_user.username+ ' was successfully deleted'

def change_user_password(form,user):
    
    user = User.query.filter_by(username=user).first()

    if user.check_password(form.current_password.data)==False:
        return False
    elif user.check_password(form.new_password.data)==True:
        return True
    else:
        user.set_password(form.new_password.data)
        db.session.add(user)
        db.session.commit()
    return 'Your password has been changed'