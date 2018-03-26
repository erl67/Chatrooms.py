from flask_sqlalchemy import SQLAlchemy 
from datetime import datetime, timedelta
from random import randrange

db = SQLAlchemy()

staffers = db.Table('staffers',
    db.Column('room_id', db.Integer, db.ForeignKey('room.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'))
)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(64), unique=False, nullable=True)
    email = db.Column(db.String(120), unique=False, nullable=True)
    currentroom = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=True)
    
    def __init__(self, username, password, email, currentroom=None):
        self.username = username
        self.password = password
        self.email = email
        self.currentroom = 0

    def __repr__(self):
        return "<User {} {}>".format(repr(self.id), repr(self.username))
    
    def Everything():
        txt = "\t" + str(User.__table__) + "\n"
        cols = User.__table__.columns.keys()
        txt += (str(cols) + "\n")
        resultSet = User.query.order_by(User.id.asc()).all()
        for item in resultSet:
            txt += ' '.join([str(getattr(item, col)) for col in cols]) +  "\n"
        return txt
    
class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    roomname = db.Column(db.String(80), unique=True, nullable=False)
    creator = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
    lastmessage = db.Column(db.DateTime, nullable=False)

    def __init__(self, roomname, creator, created, lastmessage):
        self.roomname = roomname
        self.creator = 1 if client == None else client 
        self.created = datetime.utcnow() if created == None else created 
        self.lastmessage = datetime.utcnow() if created == None else created 

    def __repr__(self):
        return "<Room {}>".format(repr(self.eventname))
    
    def Everything():
        txt = "\t" + str(Event.__table__) + "\n"
        cols = Event.__table__.columns.keys()
        txt += (str(cols) + "\n")
        resultSet = Event.query.order_by(Event.id.asc()).all()
        for item in resultSet:
            txt += ' '.join([str(getattr(item, col)) for col in cols]) +  "\n"
        return txt
 

def populateDB():
    db.session.add(User(username="owner", password="pass", email="N@A", currentroom=None))
#     db.session.add(User(username="customer", password="pass", email="customer@catering.py", staff=None))
#     db.session.add(User(username="staff", password="pass", email="staff@catering.py", staff=True))
#     db.session.add(User(username="admin", password="admin", email="admin@example.com", staff=None))
#     db.session.add(User(username="staff1", password="pass", email="staff1@catering.py", staff=True))
#     db.session.add(User(username="staff2", password="pass", email="staff2@catering.py", staff=True))
#     db.session.add(User(username="staff3", password="pass", email="staff3@catering.py", staff=True))
#     db.session.add(User(username="staff4", password="pass", email="staff4@catering.py", staff=True))
#     db.session.add(User(username="staff5", password="pass", email="staff5@catering.py", staff=True))
#     db.session.add(User(username="customer1", password="pass", email="customer1@catering.py", staff=None))
#     db.session.add(User(username="customer2", password="pass", email="customer2@catering.py", staff=None))
#     db.session.add(User(username="customer3", password="pass", email="customer3@catering.py", staff=None))
#     db.session.add(User(username="customer4", password="pass", email="customer4@catering.py", staff=None))
#     db.session.add(User(username="customer5", password="pass", email="customer5@catering.py", staff=None))
#     db.session.add(User(username="customer6", password="pass", email="customer6@catering.py", staff=None))
#     db.session.add(Event(eventname="🎉Grand Opening🍾", email="test@email", client=1, staff1=5, staff2=6, staff3=7, date=datetime.utcnow()+timedelta(days=2), created=None))
#     db.session.add(Event(eventname="🎆Grand Closing🎆", email="test2@email", client=1, staff1=5, date=datetime.utcnow()+timedelta(days=420), created=datetime.utcnow()-timedelta(days=420)))
#     db.session.add(Event(eventname="🕶️Test Party🕶️", email="test2@email", client=4, date=datetime.utcnow()+timedelta(days=randrange(100)), created=datetime.utcnow()-timedelta(days=randrange(100))))
#     db.session.add(Event(eventname="🍸Cocktail Party🍸", email="test2@email", client=10, staff1=8, staff2=9, staff3=7, date=datetime.utcnow()+timedelta(days=randrange(100)), created=datetime.utcnow()-timedelta(days=randrange(100))))
#     db.session.add(Event(eventname="🎊Confetti Event🎊", email="test2@email", client=11, date=datetime.utcnow()+timedelta(days=randrange(100)), created=datetime.utcnow()-timedelta(days=randrange(100))))
#     db.session.add(Event(eventname="🥂Champagne Testing🥂", email="test2@email", staff1=7, staff2=5, staff3=6, client=12, date=datetime.utcnow()+timedelta(days=randrange(100)), created=datetime.utcnow()-timedelta(days=randrange(100))))
#     db.session.add(Event(eventname="🎂 Birthday Party 🎂", email="test2@email", staff3=9, client=13, date=datetime.utcnow()+timedelta(days=randrange(100)), created=datetime.utcnow()-timedelta(days=randrange(100))))
#     db.session.add(Event(eventname="🎁 Birthday Party 🎁", email="test2@email", client=13, date=datetime.utcnow()+timedelta(days=randrange(100)), created=datetime.utcnow()-timedelta(days=randrange(100))))
#     db.session.add(Event(eventname="🎃Halloween Party🎃", email="test2@email", client=14, date=datetime(2018, 10, 31, 20, 0), created=datetime.utcnow()-timedelta(days=randrange(100))))
    db.session.commit()
    print('DB Populated...') 
    return True

print('Model loaded...')
