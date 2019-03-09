from app import db
from app.models import Log
pitu = Log.query.all()

for idx,event in enumerate(pitu):
	db.session.delete(event)
	db.session.commit()
