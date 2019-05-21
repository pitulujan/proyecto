from app.models import User, Scheduled_events
from app.server import delete_scheduled_event
from app import db

def create_user_full(form):

    create_user = User(username=form.username.data, admin=form.admin.data)
    create_user.set_password(form.password.data)


    db.session.add(create_user)

    db.session.commit()    
        
    return 'Congratulations, you have just registered '+form.username.data+'!'
    
def delete_user_full(user):

    delete_user = User.query.filter_by(username=user).first()
      
    shceduled_events_to_del=Scheduled_events.query.filter_by(user=user)
    
    #Agarro tods los pids del usuario que voy a eliminar y se los mando al metodo para que la libreria apscheduler se haga cargo
    
    pids=[]
    for pid in shceduled_events_to_del:
        pids.append(pid.pid)
    
    if len(pids)!=0:
        delete_scheduled_event(pids)
        db.session.delete(shceduled_events_to_del)

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