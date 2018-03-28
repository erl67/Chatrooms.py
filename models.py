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

    def __init__(self, roomname, creator=None, created=None, lastmessage=None):
        self.roomname = roomname
        self.creator = 1 if creator == None else creator 
        self.created = datetime.utcnow() if created == None else created 
        self.lastmessage = datetime.utcnow() if lastmessage == None else created 

    def __repr__(self):
        return "<Room {} {}>".format(repr(self.id), repr(self.roomname))
    
    def Everything():
        txt = "\t" + str(Room.__table__) + "\n"
        cols = Room.__table__.columns.keys()
        txt += (str(cols) + "\n")
        resultSet = Room.query.order_by(Room.id.asc()).all()
        for item in resultSet:
            txt += ' '.join([str(getattr(item, col)) for col in cols]) +  "\n"
        return txt
 
class Chat(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    room = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)
    creator = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
    message = db.Column(db.String(200), unique=False, nullable=False)


    def __init__(self, room, creator=None, created=None, message=None):
        self.room = room
        self.creator = 0 if creator == None else creator 
        self.created = datetime.utcnow() if created == None else created 
        self.message = "😶" if message == None else message

    def __repr__(self):
        return "<Chat {} {} {}>".format(repr(self.id), repr(self.room), repr(self.message))
    
    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    
    def r2d():
        return {c.name: getattr(c.value, c.name) for c in Chat.__table__.columns}
    
#     def as_json(self):
    def as_json():
#         return {c.name: getattr(self, c.name) for c in self.__table__.columns}
        json = []
        cols = Chat.__table__.columns.keys()
        resultSet = Chat.query.order_by(Chat.id.asc()).all()
        for item in resultSet:
            json += [str(getattr(item, col)) for col in cols]
        return json
    
    def Everything():
        txt = "\t" + str(Chat.__table__) + "\n"
        cols = Chat.__table__.columns.keys()
        txt += (str(cols) + "\n")
        resultSet = Chat.query.order_by(Chat.id.asc()).all()
        for item in resultSet:
            txt += ' '.join([str(getattr(item, col)) for col in cols]) +  "\n"
        return txt

def populateDB():
    db.session.add(User(username="owner", password="pass", email="N@A", currentroom=None))
    db.session.add(User(username="FirstUser", password="pass", email="N@A", currentroom=None))
    db.session.add(Room(roomname="Welcome Room", creator=None, created=datetime.utcnow(), lastmessage=datetime.utcnow()))
    db.session.add(Room(roomname="Room 1", creator=2, created=datetime(2017, 10, 31, 20, 0), lastmessage=None))
    db.session.add(Chat(room=1, creator=1, created=None, message="Test Message"))
    db.session.add(Chat(room=1, creator=2, created=None, message="First Message"))

    db.session.commit()
    print('DB Populated...') 
    return True

print('Model loaded...')
