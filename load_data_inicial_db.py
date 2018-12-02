from app import db
from app.models import User

pitu = User(username='Pitu',admin=True)
pitu.set_password('pitu')
gordo =User(username='gordo',admin=False)
gordo.set_password('gordo')
db.session.add(pitu)
db.session.add(gordo)
db.session.commit()



