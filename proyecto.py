from app import app, db,socketio
from app.models import User

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User}


if __name__ == '__main__':
	socketio.run(app,host='0.0.0.0', port=5000)#,debug=True,use_reloader=False)