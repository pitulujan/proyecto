from app.models import User, User_State
from app import app, db

def create_user_full(form):

    create_user = User(username=form.username.data, admin=form.admin.data)
    create_user.set_password(form.password.data)
    db.session.add(create_user)
    db.session.commit()

    id_us= User.query.filter_by(username=form.username.data).first()
   
    create_state = User_State(user_id=id_us.id,light_state=False,light_intensity=10, temp_state=20.0)
    db.session.add(create_state)
    db.session.commit()    
        
    return 'Congratulations, you have just registered '+form.username.data+'!'
    
def delete_user_full(user):

    delete_user = User.query.filter_by(username=user).first()
    state_to_del= User_State.query.filter_by(user_id=delete_user.id).first()   
    db.session.delete(delete_user)
    db.session.delete(state_to_del)
    db.session.commit()

    return 'Congratulations, you have just deleted '+delete_user.username+ ' from the users list!'