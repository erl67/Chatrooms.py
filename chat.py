#erl67
REBUILD_DB = False
FDEBUG = False

import os, re, json
from sys import stderr
from flask import Flask, g, send_from_directory, flash, render_template, abort, request, redirect, url_for, session, Response, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy import or_
from datetime import datetime, date, timedelta
from dateutil import parser
from random import getrandbits
from models import db, populateDB, User, Room, Chat

def create_app():
    app = Flask(__name__)
    DB_NAME = os.path.join(app.root_path, 'chat.db')
    
    app.config.update(dict(
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SECRET_KEY='erl67_',
        TEMPLATES_AUTO_RELOAD=True,
        USE_threaded = True,
        SQLALCHEMY_DATABASE_URI='sqlite:///' + DB_NAME
    ))
    
    db.init_app(app)
    
    if REBUILD_DB == True and os.access(DB_NAME, os.W_OK):
        os.remove(DB_NAME)
        print('DB Dropped')
        
    if os.access(DB_NAME, os.W_OK):
        print('DB Exists')
    else:
        app.app_context().push()
        db.drop_all()
        db.create_all()
        print('DB Created')
        populateDB()
    print(app.__str__(), end="  ")
    return app

app = create_app()

@app.cli.command('initdb')
def initdb_command():
    db.drop_all()
    db.create_all()
    populateDB()
    print('Initialized the database.')
    
@app.before_request
def before_request():
    g.user = None
    g.rooms = None
    g.chats = None
    g.jchats = None
    g.others = None
    if 'uid' in session:
        g.user = User.query.filter_by(id=session['uid']).first()
        if g.user != None:
            g.rooms = Room.query.order_by(Room.lastmessage.asc()).all()
            if g.user.currentroom > 0:
                g.chats = Chat.query.filter(Chat.room == g.user.currentroom).order_by(Chat.created.asc()).all()
                g.jchats = Chat.as_json(g.user.currentroom)
                g.others = [u.username for u in User.query.filter(User.currentroom == g.user.currentroom).all()]
            else:
                g.chats = Chat.query.limit(10).all()
                g.jchats = Chat.as_json()
#     eprint("g.user: " + str(g.user))
#     eprint("g.rooms: " + str(g.rooms))
#     eprint("g.chats: " + str(g.chats))
#     eprint("g.jchats: " + str(g.jchats))
#     eprint("g.others: " + str(g.others))
    
        
@app.before_first_request
def before_first_request():
    eprint("    🥇")
    
@app.context_processor
def utility_processor():
    def getName(id):
        user = User.query.filter(User.id==id).first()
        if user != None:
            return user.username
        else:
            return ""
    return dict(getName=getName)

@app.context_processor
def utility_processor():
    def getRoom(id):
        room = Room.query.filter(Room.id==id).first()
        if room != None:
            return room.roomname
        else:
            return ""
    return dict(getRoom=getRoom)


@app.route("/register/", methods=["GET", "POST"])
def signer():
    if g.user:
        flash("Already logged in!")
        return redirect(url_for("index"))
    #elif request.method == "GET":
        #flash("Complete form to register")
    elif request.method == "POST":
        POST_USER = remove_tags(str(request.form['user']))
        POST_PASS = remove_tags(str(request.form['pass']))
        POST_EMAIL = remove_tags(str(request.form['mail']))
        if POST_USER != None and POST_PASS != None:
            newUser = User(POST_USER, POST_PASS, POST_EMAIL)
            db.session.add(newUser)
            try:
                db.session.commit()
                if User.query.filter(User.username == POST_USER, User.password == POST_PASS):
                    flash("Successfully registered! " + POST_USER + ":" + POST_PASS)
                    session["uid"] = User.query.filter(User.username == POST_USER).first().id
                    return redirect(url_for("index"))
            except Exception as e:
                db.session.rollback()
                eprint(str(e))
                flash("Error adding to database")
        else:
            flash("Error registering new account")
    return Response(render_template("accounts/newAccount.html"), status=200, mimetype='text/html')

@app.route("/login/", methods=["GET", "POST"])
def logger():
    if "uid" in session:
        flash("Already logged in!")
        return redirect(url_for("index"))
    elif request.method == "POST":
        POST_USER = str(request.form['user'])
        POST_PASS = str(request.form['pass'])
        valid = User.query.filter(User.username == POST_USER, User.password == POST_PASS).first()
        eprint(str(valid))
        if (POST_USER == "owner") and (POST_PASS == "pass"):
            session["uid"] = 1
            flash("Successfully logged in as Mr. Manager")
            return redirect(url_for("rooms"))
        elif valid is not None:
            session["uid"] = valid.id
            flash("Successfully logged in!  " + valid.username)
            return redirect(url_for("rooms", uid=valid.id))
        else:
            flash("Error logging you in!")
    return Response(render_template("accounts/loginPage.html"), status=200, mimetype='text/html')

@app.route("/logout/")
def unlogger():
    if "uid" in session:
        session.clear()
        flash("Successfully logged out!")
        return redirect(url_for("index"))
    else:
        session.clear()
        flash("Not currently logged in!")
        return redirect(url_for("logger"))
    
@app.route("/db/")
def rawstats():
    msg = ""
    msg += User.Everything()
    msg += "\n\n"
    msg += Room.Everything()
    msg += "\n\n"
    msg += Chat.Everything()
    return Response(render_template('test.html', testMessage=msg), status=203, mimetype='text/html')

@app.route('/')
def index():
    return Response(render_template('index.html'), status=200, mimetype='text/html')

@app.route('/rooms/')
def rooms():
    if g.user.currentroom == 0:
        return redirect(url_for("index"))
    else: 
        return redirect(url_for("joinroom", rid=g.user.currentroom))
    abort(404)
    
@app.route("/deleteroom/", methods=["GET", "POST"])
def rmroom():
    if not g.user:
        abort(404)
    if request.method == "POST":
        roomId = g.user.currentroom
        if roomId != None:
            room = Room.query.filter(Room.id==int(roomId)).first()
            try:
                db.session.commit()
                db.session.delete(room)
                Chat.query.filter(Chat.room == roomId).delete()
                User.query.filter(User.currentroom == roomId).update({'currentroom': 0})
                db.session.commit()
                flash("Deleted room")
            except Exception as e:
                db.session.rollback()
                eprint(str(e))
                flash("Error deleting room")
            return redirect(url_for("index"))
        else:
            flash("Cannot find room to delete")
            abort(404)
    else:
        abort(404)

@app.route('/room/<int:rid>')
def joinroom(rid=None):
    if (not g.user or not rid):
        abort(404)
    elif (g.user.currentroom == rid):
        eprint(g.user.currentroom)
        room = Room.query.filter(Room.id == rid).first()
        chats = g.chats
        return Response(render_template('/rooms/room.html', room=room, chats=chats, others=g.others), mimetype='text/html')
    else:
        room = Room.query.filter(Room.id == rid).first()
        if room == None:
            abort(404)
        else:
            chats = Chat.query.filter(Chat.room == room.id).order_by(Chat.created.asc()).all()
            user = User.query.filter(User.id == g.user.id).first()
            user.currentroom = room.id
            db.session.commit()
            others = [u.username for u in User.query.filter(User.currentroom == g.user.currentroom).all()]

            return Response(render_template('/rooms/room.html', room=room, chats=chats, others=others), mimetype='text/html')
    return redirect(url_for("index"))

@app.route('/leaveroom/')
def exitroom():
    if not g.user:
        abort(404)
    else:
        user = User.query.filter(User.id == g.user.id).first()
        user.currentroom = 0
        try:
            db.session.commit()
            flash("Left room")
        except Exception as e:
            db.session.rollback()
            eprint (str(e))
            flash("Error leaving room")
    return redirect(url_for("index"))

@app.route('/newroom/', methods=["GET", "POST"])
def newroom():
    if not g.user:
        abort(404)
    elif request.method == "POST":
        POST_ROOM = remove_tags(str(request.form['room']))
        POST_CHAT = remove_tags(str(request.form['msg']))
        if POST_CHAT != None:
            newRoom = Room(POST_ROOM, g.user.id, None, None)
            eprint("newRoom: " + str(newRoom))
            db.session.add(newRoom)
            try:
                db.session.commit()
                newChat = Chat(newRoom.id, g.user.id, None, POST_CHAT)
                eprint("newChat: " + str(newChat))
                db.session.add(newChat)
                try:
                    db.session.commit()
                    flash ("Created room: " + str(newRoom.roomname))
                    return redirect(url_for("joinroom", rid=newRoom.id))
                except Exception as e:
                    db.session.rollback()
                    eprint(str(e))
                    flash("Error adding message to new room")
                    return redirect(url_for("newroom"))
            except Exception as e:
                flash("Room creation failed")
        else:
            flash("Must enter initial message")
    return Response(render_template('/rooms/newRoom.html'), mimetype='text/html')

@app.route('/r')
def get_room():
    if g.user:
        return json.dumps(g.user.currentroom, default=json_serial)
    else:
        abort(404)
        
@app.route('/u')
def get_user():
    if g.user:
        return json.dumps(g.user.username, default=json_serial)
    else:
        abort(404)
        
@app.route("/chats")
def get_chats():
    if g.user:
        chatsJSON = Chat.as_json(g.user.currentroom)
        chats = len(chatsJSON)
        eprint ("chats: " + str(chats))
        if chats == 0:
            flash("room no longer exists")
            return redirect(url_for("index"))
        else:
            return str(chats)
    else:
        abort(404)

@app.route("/updates/<int:count>", methods=["POST", "GET"]) #remove get after testing 
def get_updates(count=None):
    if g.user:
        updates = Chat.as_jsonUpdates(g.user.currentroom, count)
        eprint("updates" + str(updates))
        return json.dumps(updates, default=json_serial)
    else:
        abort(404)

@app.route('/chat')
def get_chat():
    return json.dumps(g.jchats, default=json_serial)

@app.route("/new_msg", methods=["POST"])
def add():
    eprint(str(request.json))
    message = request.json["msg"]
    message = remove_tags(message)
    newChat = Chat(g.user.currentroom, g.user.id, None, message)
    db.session.add(newChat)
    try:
        db.session.commit()
        flash ("Message received")
        return ('', 204)
    except Exception as e:
        db.session.rollback()
        flash("Error receiving message")
        return ('', 510)

@app.route('/ajax.js')
def ajax():
    return Response(render_template('ajax.js'), status=200, mimetype='application/javascript')

@app.errorhandler(403)
@app.errorhandler(404)
def page_not_found(error):
    return Response(render_template('404.html', errno=error), status=404, mimetype='text/html')

@app.errorhandler(405)
def wrong_method(error):
    return Response("You shouldn't have done that", status=405, mimetype='text/html')

@app.route('/418/')
def err418(error=None):
    return Response(render_template('404.html', errno=error), status=418, mimetype='text/html')

@app.route('/favicon.ico') 
def favicon():
    if bool(getrandbits(1))==True:
        return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')
    else:
        return send_from_directory(os.path.join(app.root_path, 'static'), 'faviconF.ico', mimetype='image/vnd.microsoft.icon')

def eprint(*args, **kwargs):
    print(*args, file=stderr, **kwargs)
    
TAG_RE = re.compile(r'<[^>]+>')
def remove_tags(text):
    return TAG_RE.sub('', text)

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code stackoverflow.com/a/22238613/7491839 """
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError ("Type %s not serializable" % type(obj))
    
if __name__ == "__main__":
    print('Starting......')
    if FDEBUG==True:
        app.config.update(dict(
            DEBUG=True,
            DEBUG_TB_INTERCEPT_REDIRECTS=False,
            SQLALCHEMY_TRACK_MODIFICATIONS=True,
            TEMPLATES_AUTO_RELOAD=True,
        ))
        app.jinja_env.auto_reload = True
        toolbar = DebugToolbarExtension(app) 
        app.run(use_reloader=True, host='0.0.0.0')
    else:
        app.run()